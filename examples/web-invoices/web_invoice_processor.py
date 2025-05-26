#!/usr/bin/env python3
"""
Web Invoice Processor

This script retrieves invoices from various provider websites and organizes them
in a structured directory layout.
"""
import os
import re
import json
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebInvoiceProcessor:
    """Processes invoices from various web providers."""
    
    def __init__(self, config: Dict):
        """Initialize with configuration."""
        self.config = config
        self.output_dir = Path(config['output_dir'])
        self.year = config.get('year', datetime.now().year)
        self.month = config.get('month', datetime.now().month)
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def process_provider(self, provider: str, credentials: Dict) -> List[Dict]:
        """Process invoices for a specific provider."""
        try:
            # Get the appropriate processor method for this provider
            processor_name = f"_process_{provider.lower()}"
            if not hasattr(self, processor_name):
                logger.warning(f"No processor implemented for provider: {provider}")
                return []
            
            processor = getattr(self, processor_name)
            logger.info(f"Processing invoices for {provider}...")
            
            # Process the provider and get invoice data
            invoice_data = processor(credentials)
            
            # Save the invoices
            saved_invoices = []
            for invoice in invoice_data:
                saved_invoice = self._save_invoice(provider, invoice)
                if saved_invoice:
                    saved_invoices.append(saved_invoice)
            
            logger.info(f"Processed {len(saved_invoices)} invoices from {provider}")
            return saved_invoices
            
        except Exception as e:
            logger.error(f"Error processing {provider}: {e}", exc_info=True)
            return []
    
    def _save_invoice(self, provider: str, invoice: Dict) -> Optional[Dict]:
        """Save an invoice and its metadata."""
        try:
            # Create directory structure: output/YYYY-MM/provider/invoices/
            provider_dir = self.output_dir / f"{self.year:04d}-{self.month:02d}" / provider.lower()
            invoice_dir = provider_dir / 'invoices'
            invoice_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate a safe filename
            invoice_number = re.sub(r'[^\w-]', '_', invoice.get('invoice_number', 'invoice'))
            filename = f"{invoice_number}{invoice.get('extension', '.pdf')}"
            filepath = invoice_dir / filename
            
            # Download the invoice file if URL is provided
            if 'download_url' in invoice and invoice['download_url']:
                response = self.session.get(invoice['download_url'], stream=True)
                response.raise_for_status()
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            # If content is provided directly
            elif 'content' in invoice and invoice['content']:
                with open(filepath, 'w' if isinstance(invoice['content'], str) else 'wb') as f:
                    f.write(invoice['content'])
            else:
                logger.warning("No content or download URL provided for invoice")
                return None
            
            # Prepare metadata
            metadata = {
                'provider': provider,
                'invoice_number': invoice.get('invoice_number'),
                'invoice_date': invoice.get('invoice_date'),
                'amount': invoice.get('amount'),
                'currency': invoice.get('currency', 'USD'),
                'download_url': invoice.get('download_url'),
                'saved_path': str(filepath.relative_to(self.output_dir)),
                'download_time': datetime.now().isoformat(),
                'file_size': os.path.getsize(filepath),
                'metadata': invoice.get('metadata', {})
            }
            
            # Save metadata as JSON
            metadata_path = filepath.with_suffix('.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved invoice: {filepath}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error saving invoice: {e}")
            return None
    
    def _process_example_provider(self, credentials: Dict) -> List[Dict]:
        """Example implementation for a provider.
        
        This is a template that would be implemented for each specific provider.
        """
        invoices = []
        
        try:
            # Example: Log in to the provider's API
            login_url = "https://api.example.com/auth/login"
            response = self.session.post(
                login_url,
                json={
                    'username': credentials.get('username'),
                    'password': credentials.get('password')
                }
            )
            response.raise_for_status()
            
            # Get list of invoices
            invoices_url = "https://api.example.com/invoices"
            response = self.session.get(invoices_url)
            response.raise_for_status()
            
            # Process each invoice
            for invoice in response.json():
                invoice_date = datetime.strptime(invoice['date'], '%Y-%m-%d')
                
                # Filter by target month
                if (invoice_date.year == self.year and 
                    invoice_date.month == self.month):
                    
                    invoices.append({
                        'invoice_number': invoice['id'],
                        'invoice_date': invoice['date'],
                        'amount': invoice['amount'],
                        'currency': invoice['currency'],
                        'download_url': f"https://api.example.com/invoices/{invoice['id']}/download",
                        'metadata': {
                            'status': invoice.get('status'),
                            'due_date': invoice.get('due_date')
                        }
                    })
            
        except Exception as e:
            logger.error(f"Error processing example provider: {e}")
        
        return invoices
    
    # Add more provider-specific methods here
    # Example: _process_aws(), _process_google_cloud(), etc.

def load_config() -> Dict:
    """Load configuration from config file."""
    config_path = Path(__file__).parent / 'config' / 'config.json'
    with open(config_path, 'r') as f:
        return json.load(f)

def main():
    """Main function."""
    try:
        # Load configuration
        config = load_config()
        
        # Create and run processor
        processor = WebInvoiceProcessor(config)
        
        # Process each provider
        results = {}
        for provider, credentials in config.get('providers', {}).items():
            if credentials.get('enabled', True):
                results[provider] = processor.process_provider(provider, credentials)
        
        # Print summary
        print("\n=== Processing Complete ===")
        for provider, invoices in results.items():
            print(f"{provider}: {len(invoices)} invoices processed")
        
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
