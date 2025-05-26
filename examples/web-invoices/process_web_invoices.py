#!/usr/bin/env python3
"""
Web Invoice Processor

This script retrieves invoices from various provider websites and organizes them
in a structured directory layout using the shared configuration system.
"""
import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

# Add shared directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import shared utilities
from shared import load_config, ConfigLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebInvoiceProcessor:
    """Processor for retrieving invoices from various web providers."""
    
    def __init__(self, config: Optional[Union[ConfigLoader, Dict[str, Any]]] = None, **kwargs):
        """Initialize the web invoice processor.
        
        Args:
            config: Optional ConfigLoader instance or dict with configuration
            **kwargs: Additional configuration overrides
        """
        # Initialize configuration
        if config is None:
            self.config = load_config(env_prefix='WEB_', **kwargs)
        elif isinstance(config, dict):
            self.config = load_config(env_prefix='WEB_', **{**config, **kwargs})
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
        self.year = self.config.get_int('year')
        self.month = self.config.get_int('month')
        
        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def get_available_providers(self) -> List[str]:
        """Get a list of available provider names."""
        # This will be populated from configuration or discovered providers
        providers = self.config.get('providers', [])
        if isinstance(providers, str):
            providers = [p.strip() for p in providers.split(',')]
        return providers
    
    def process_provider(self, provider_name: str) -> bool:
        """Process invoices for a specific provider."""
        try:
            logger.info(f"Processing invoices for provider: {provider_name}")
            # TODO: Implement provider-specific processing
            return True
        except Exception as e:
            logger.error(f"Error processing provider {provider_name}: {e}")
            return False
    
    def process_all_providers(self) -> Dict[str, bool]:
        """Process invoices for all available providers."""
        results = {}
        for provider in self.get_available_providers():
            results[provider] = self.process_provider(provider)
        return results

def main():
    """Main function."""
    try:
        # Load configuration from multiple sources
        config = load_config(
            env_path=Path(__file__).parent / '.env',
            json_path=Path(__file__).parent / 'config' / 'config.json',
            env_prefix='WEB_'
        )
        
        # Set up logging
        log_level = config.get('log_level', 'INFO').upper()
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename=config.get('log_file')
        )
        
        logger.info(f"Starting web invoice processor for {config.get_int('year')}-{config.get_int('month'):02d}")
        
        # Create and run processor
        processor = WebInvoiceProcessor(config)
        results = processor.process_all_providers()
        
        # Log results
        for provider, success in results.items():
            status = "succeeded" if success else "failed"
            logger.info(f"Processing for provider '{provider}' {status}")
        
        logger.info("Processing completed")
        return 0 if all(results.values()) else 1
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
