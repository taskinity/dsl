# Web Invoice Processor

This is a web invoice processor that demonstrates how to use the Taskinity DSL for processing invoices from various cloud providers with local processing.

## Features

- Supports multiple cloud providers (AWS, Google Cloud, Azure)
- Downloads and processes invoices locally
- Extracts invoice data to structured format
- Configurable through YAML and environment variables
- Local processing with no external API dependencies

## Directory Structure

```
output/
└── YYYY-MM/                    # Year and month of invoices
    └── provider_name/          # Provider name (e.g., aws, google_cloud)
        └── invoices/          # Directory containing invoice files
            ├── invoice_123.pdf  # The actual invoice file
            └── invoice_123.json # Metadata about the invoice
```

## Prerequisites

- Python 3.8+
- Tesseract OCR (for text extraction from images/PDFs if needed)
- Poppler (for PDF processing)
- Make

## Installation

1. Install system dependencies:

   On Ubuntu/Debian:

   ```bash
   sudo apt update
   sudo apt install tesseract-ocr poppler-utils
   ```

   On macOS (using Homebrew):

   ```bash
   brew install tesseract poppler
   ```

2. Set up the development environment using Make:

   ```bash
   make setup
   ```

   This will:

   - Create a Python virtual environment
   - Install all required dependencies
   - Set up development tools

## Configuration

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your provider credentials and settings. Here's an example configuration:

   ```ini
   # General Settings
   YEAR=2025
   MONTH=5
   OUTPUT_DIR=./output
   LOG_LEVEL=INFO
   LOG_FILE=web_invoice_processor.log

   # Example Provider
   EXAMPLE_PROVIDER_USERNAME=your_username
   EXAMPLE_PROVIDER_PASSWORD=your_password

   # AWS Provider
   AWS_ACCESS_KEY_ID=your_aws_access_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key

   # Google Cloud Provider
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

   # Azure Provider
   AZURE_SUBSCRIPTION_ID=your_subscription_id
   AZURE_CLIENT_ID=your_client_id
   AZURE_CLIENT_SECRET=your_client_secret
   AZURE_TENANT_ID=your_tenant_id
   ```

   > **Note**: Only include the configuration sections for the providers you plan to use.

## Usage

### Using Make (recommended)

```bash
# List available providers
make providers

# Run the processor for all enabled providers
make run

# Run with specific month and year
YEAR=2025 MONTH=5 make run

# Run for a specific provider
PROVIDER=aws make run
```

### Direct Python execution

```bash
# Activate the virtual environment
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Run the processor
python web_invoice_processor.py

# Or with environment variables
YEAR=2025 MONTH=5 PROVIDER=aws python web_invoice_processor.py
```

## Makefile Commands

The Makefile provides several useful commands:

```bash
make setup       # Set up the development environment
make install     # Install the package in development mode
make test        # Run tests
make lint        # Run code style checks
make format      # Format the code
make providers   # List available providers
make run         # Run the web invoice processor
make clean       # Clean up temporary files
```

## Adding a New Provider

To add support for a new provider:

1. Create a new method in the `WebInvoiceProcessor` class following this pattern:

   ```python
   def _process_PROVIDER_NAME(self, credentials: Dict) -> List[Dict]:
       """Process invoices from PROVIDER_NAME."""
       invoices = []

       try:
           # 1. Authenticate with the provider's API/website
           # 2. Retrieve list of invoices for the target month
           # 3. For each invoice, collect:
           #    - Invoice number
           #    - Invoice date
           #    - Amount
           #    - Download URL
           #    - Any additional metadata

           # Example:
           invoice_data = {
               'invoice_number': 'INV-123',
               'invoice_date': '2025-05-15',
               'amount': 99.99,
               'currency': 'USD',
               'download_url': 'https://example.com/invoices/123',
               'metadata': {
                   'status': 'paid',
                   'due_date': '2025-06-15'
               }
           }
           invoices.append(invoice_data)

       except Exception as e:
           logger.error(f"Error processing PROVIDER_NAME: {e}")

       return invoices
   ```

2. Add the provider's configuration to `config/config.json`.

## Error Handling

- The processor will log errors and continue processing other providers if one fails
- Check the console output for detailed error messages
- Failed downloads will be logged but won't stop the entire process

## Security Notes

- Never commit your `.env` file to version control
- The `.env.example` file is versioned, but the actual `.env` is in `.gitignore`
- Use environment variables for sensitive information
- The virtual environment directory (`venv/`) is also in `.gitignore`
- Consider using a secrets manager in production environments

## License

This project is licensed under the MIT License - see the LICENSE file for details.
