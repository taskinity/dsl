"""
Email Invoice Processor

This module provides functionality to process emails, extract invoice attachments,
and save them in a structured format.
"""

import imaplib
import email
import os
import logging
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmailProcessor:
    """
    A class to process emails and extract invoice attachments.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the EmailProcessor with configuration.

        Args:
            config: A dictionary containing configuration settings
        """
        self.config = config
        self.mail = None
        self._ensure_output_dirs()

    def _ensure_output_dirs(self) -> None:
        """Ensure that output directories exist."""
        os.makedirs(self.config.get('output_dir', 'output'), exist_ok=True)

    def _connect_email(self) -> None:
        """
        Connect to the email server using IMAP.

        Raises:
            RuntimeError: If connection to the email server fails
        """
        try:
            self.mail = imaplib.IMAP4_SSL(
                self.config['email']['server'],
                self.config['email']['port']
            )
            self.mail.login(
                self.config['email']['username'],
                self.config['email']['password']
            )
            logger.info("Successfully connected to email server")
        except Exception as e:
            logger.error(f"Failed to connect to email server: {e}")
            raise RuntimeError(f"Failed to connect to email server: {e}") from e

    def _process_attachment(self, part: email.message.Message) -> None:
        """
        Process an email attachment.

        Args:
            part: The email part containing the attachment
        """
        filename = part.get_filename()
        if not filename:
            return

        # Save the attachment
        filepath = os.path.join(
            self.config.get('output_dir', 'output'),
            filename
        )
        
        try:
            with open(filepath, 'wb') as f:
                f.write(part.get_payload(decode=True))
            logger.info(f"Saved attachment: {filename}")
        except Exception as e:
            logger.error(f"Failed to save attachment {filename}: {e}")

    def process_emails(self) -> None:
        """
        Process all emails in the configured folder.
        """
        if not self.mail:
            raise RuntimeError("Not connected to email server. Call _connect_email() first.")

        try:
            # Select the folder to process
            self.mail.select(self.config['email'].get('folder', 'INBOX'))
            
            # Search for all emails
            status, messages = self.mail.search(None, 'ALL')
            if status != 'OK':
                logger.error("Failed to search emails")
                return

            # Process each email
            for num in messages[0].split():
                status, data = self.mail.fetch(num, '(RFC822)')
                if status != 'OK':
                    logger.error(f"Failed to fetch email {num.decode()}")
                    continue

                raw_email = data[0][1]
                email_message = email.message_from_bytes(raw_email)

                # Process each part of the email
                for part in email_message.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue
                    
                    self._process_attachment(part)

                # Move to processed folder if configured
                if 'processed_folder' in self.config['email']:
                    self.mail.copy(num, self.config['email']['processed_folder'])
                    self.mail.store(num, '+FLAGS', '\\Deleted')
            
            # Expunge deleted messages
            self.mail.expunge()

        except Exception as e:
            logger.error(f"Error processing emails: {e}")
            raise

    def run(self) -> None:
        """
        Run the email processing pipeline.
        """
        try:
            self._connect_email()
            self.process_emails()
        except Exception as e:
            logger.error(f"Error in email processing pipeline: {e}")
            raise
        finally:
            if self.mail:
                try:
                    self.mail.close()
                    self.mail.logout()
                except Exception as e:
                    logger.error(f"Error closing email connection: {e}")


def main():
    """Main entry point for the email processor."""
    import argparse
    import yaml
    
    parser = argparse.ArgumentParser(description='Process email invoices.')
    parser.add_argument('--config', type=str, default='config.yaml',
                        help='Path to configuration file')
    
    args = parser.parse_args()
    
    try:
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
        
        processor = EmailProcessor(config)
        processor.run()
        
    except Exception as e:
        logger.error(f"Failed to run email processor: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
