#!/usr/bin/env python3
"""
Email Invoice Processor

This script connects to an email account, retrieves emails from a specific month,
extracts attachments, and organizes them in a structured directory layout.
"""
import os
import re
import json
import imaplib
import email
import email.header
import logging
import sys
from email.utils import parsedate_to_datetime
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

# Add shared directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import shared utilities
from shared import load_config

# Third-party imports
try:
    import pytesseract
    from pdf2image import convert_from_bytes
    import cv2
    import numpy as np
    HAS_OCR_DEPS = True
except ImportError:
    HAS_OCR_DEPS = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmailInvoiceProcessor:
    def __init__(self, config=None, **kwargs):
        """Initialize with configuration.
        
        Args:
            config: Optional ConfigLoader instance or dict with configuration
            **kwargs: Additional configuration overrides
        """
        # Initialize configuration
        if config is None:
            from shared import load_config
            self.config = load_config(env_prefix='EMAIL_', **kwargs)
        elif isinstance(config, dict):
            from shared import load_config
            self.config = load_config(env_prefix='EMAIL_', **{**config, **kwargs})
        else:
            self.config = config
            
        # Set up logging
        log_level = self.config.get('log_level', 'INFO').upper()
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename=self.config.get('log_file')
        )
        
        # Initialize instance variables
        self.output_dir = Path(self.config.get('output_dir', './output'))
        self.year = self.config.get_int('year', datetime.now().year)
        self.month = self.config.get_int('month', datetime.now().month)
        self.supported_extensions = {'.pdf', '.jpg', '.jpeg', '.png'}
        
        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Connect to email server
        self.mail = self._connect_email()
    
    def _connect_email(self) -> imaplib.IMAP4_SSL:
        """Connect to the email server."""
        try:
            server = self.config.get('imap_server')
            port = self.config.get_int('imap_port', 993)
            username = self.config.get('username') or self.config.get('email')
            password = self.config.get('password')
            
            if not all([server, username, password]):
                raise ValueError("Missing required email configuration (server, username, password)")
                
            mail = imaplib.IMAP4_SSL(server, port)
            mail.login(username, password)
            mail.select('inbox')
            logger.info("Successfully connected to email server")
            return mail
        except Exception as e:
            logger.error(f"Failed to connect to email server: {e}")
            raise
    
    def _get_email_date(self, email_message: email.message.Message) -> Optional[datetime]:
        """Extract date from email."""
        date_str = email_message.get('Date')
        if not date_str:
            return None
        try:
            return parsedate_to_datetime(date_str)
        except Exception as e:
            logger.warning(f"Failed to parse email date: {e}")
            return None
    
    def _is_target_month(self, email_date: datetime) -> bool:
        """Check if email is from target month."""
        return email_date.year == self.year and email_date.month == self.month
    
    def _extract_sender_domain(self, email_message: email.message.Message) -> str:
        """Extract domain from sender's email address."""
        sender = email_message.get('From', '')
        match = re.search(r'<([^>]+)>', sender)
        if match:
            email_address = match.group(1).lower()
        else:
            email_address = sender.lower()
        
        # Extract domain part
        domain = email_address.split('@')[-1] if '@' in email_address else 'unknown'
        return domain.replace('.', '_')
    
    def _extract_text_from_image(self, image_data: bytes) -> str:
        """Extract text from image using OCR."""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding to preprocess the image
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # Perform OCR
            text = pytesseract.image_to_string(gray)
            return text.strip()
        except Exception as e:
            logger.error(f"Error in OCR processing: {e}")
            return ""
    
    def _extract_text_from_pdf(self, pdf_data: bytes) -> str:
        """Extract text from PDF using OCR."""
        try:
            # Convert PDF to images
            images = convert_from_bytes(pdf_data)
            
            # Extract text from each page
            texts = []
            for i, image in enumerate(images):
                # Convert PIL Image to OpenCV format
                open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
                
                # Apply thresholding
                gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
                
                # Perform OCR
                text = pytesseract.image_to_string(gray)
                texts.append(text.strip())
            
            return "\n--- PAGE BREAK ---\n".join(texts)
        except Exception as e:
            logger.error(f"Error in PDF processing: {e}")
            return ""
    
    def _process_attachment(self, part, sender_domain: str) -> Optional[Dict]:
        """Process an email attachment."""
        filename = part.get_filename()
        if not filename:
            return None
        
        # Check file extension
        ext = os.path.splitext(filename)[1].lower()
        if ext not in self.supported_extensions:
            logger.debug(f"Skipping unsupported file type: {filename}")
            return None
        
        # Create a safe filename
        safe_filename = re.sub(r'[^\w\-_. ]', '_', filename)
        
        # Create directory structure: year-month/sender_domain/invoices/
        invoice_dir = self.output_dir / f"{self.year:04d}-{self.month:02d}" / sender_domain / "invoices"
        invoice_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the attachment
        file_path = invoice_dir / safe_filename
        with open(file_path, 'wb') as f:
            f.write(part.get_payload(decode=True))
        
        # Extract text based on file type
        file_data = part.get_payload(decode=True)
        extracted_text = ""
        
        if ext == '.pdf':
            extracted_text = self._extract_text_from_pdf(file_data)
        else:  # Image file
            extracted_text = self._extract_text_from_image(file_data)
        
        # Create metadata
        metadata = {
            'original_filename': filename,
            'saved_path': str(file_path.relative_to(self.output_dir)),
            'extracted_text': extracted_text,
            'processing_time': datetime.now().isoformat(),
            'file_size': len(file_data),
            'file_type': ext.lstrip('.').upper()
        }
        
        # Save metadata as JSON
        metadata_filename = f"{os.path.splitext(safe_filename)[0]}.json"
        metadata_path = invoice_dir / metadata_filename
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Processed attachment: {filename}")
        return metadata
    
    def process_emails(self):
        """Process emails from the specified month."""
        try:
            # Search for emails from the target month
            date_str = f"{self.year}-{self.month:02d}"
            search_criteria = f'(SINCE "01-{self.month:02d}-{self.year}" BEFORE "01-{self.month+1 if self.month < 12 else 1}-{self.year + (0 if self.month < 12 else 1)}")'
            
            logger.info(f"Searching for emails with criteria: {search_criteria}")
            status, messages = self.mail.uid('search', None, search_criteria)
            
            if status != 'OK':
                logger.error("Failed to search emails")
                return
            
            email_ids = messages[0].split()
            logger.info(f"Found {len(email_ids)} emails to process")
            
            # Process each email
            for email_id in email_ids:
                try:
                    # Fetch the email
                    status, msg_data = self.mail.uid('fetch', email_id, '(RFC822)')
                    if status != 'OK':
                        logger.warning(f"Failed to fetch email {email_id}")
                        continue
                    
                    # Parse the email
                    raw_email = msg_data[0][1]
                    email_message = email.message_from_bytes(raw_email)
                    
                    # Check email date
                    email_date = self._get_email_date(email_message)
                    if not email_date or not self._is_target_month(email_date):
                        continue
                    
                    # Extract sender domain for directory structure
                    sender_domain = self._extract_sender_domain(email_message)
                    
                    # Process attachments
                    for part in email_message.walk():
                        if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
                            continue
                        
                        self._process_attachment(part, sender_domain)
                    
                except Exception as e:
                    logger.error(f"Error processing email {email_id}: {e}")
                    continue
            
            logger.info("Finished processing all emails")
            
        except Exception as e:
            logger.error(f"Error in process_emails: {e}")
            raise
        finally:
            # Close the connection
            try:
                self.mail.close()
                self.mail.logout()
            except:
                pass

def main():
    """Main function."""
    try:
        # Load configuration from multiple sources
        config = load_config(
            env_path=Path(__file__).parent / '.env',
            json_path=Path(__file__).parent / 'config' / 'config.json',
            env_prefix='EMAIL_'
        )
        
        # Set up logging
        log_level = config.get('log_level', 'INFO').upper()
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename=config.get('log_file')
        )
        
        logger.info(f"Starting email invoice processor for {config.get_int('year')}-{config.get_int('month'):02d}")
        
        # Create and run processor
        processor = EmailInvoiceProcessor(config)
        processor.process_emails()
        
        logger.info("Processing completed successfully")
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
