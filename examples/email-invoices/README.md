# Email Invoice Processor

This utility processes email attachments (invoices, receipts, etc.) from a specified month, extracts text using OCR, and organizes them in a structured directory layout.

## Features

- Connects to IMAP email server
- Processes emails from a specific month
- Extracts attachments (PDF, JPG, JPEG, PNG)
- Performs OCR to extract text from images and PDFs
- Organizes files in a structured directory layout:
  ```
  output/
  └── YYYY-MM/
      └── sender_domain/
          └── invoices/
              ├── original_file.pdf
              └── original_file.json  # Contains extracted text and metadata
  ```
- Generates metadata JSON for each processed file

## Prerequisites

- Python 3.8+
- Tesseract OCR engine installed on your system
- Poppler tools (for PDF processing)
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

2. Edit `.env` with your email credentials and settings:
   ```ini
   # Email Server Configuration
   EMAIL_SERVER=imap.example.com
   EMAIL_PORT=993
   EMAIL_USERNAME=your_email@example.com
   EMAIL_PASSWORD=your_app_specific_password
   
   # Processing Settings
   YEAR=2025
   MONTH=5
   OUTPUT_DIR=./output
   
   # OCR Settings
   TESSERACT_CMD=/usr/bin/tesseract
   
   # Logging
   LOG_LEVEL=INFO
   LOG_FILE=email_processor.log
   ```

   > **Note**: For Gmail, you'll need to generate an App Password if you have 2FA enabled.

## Usage

### Using Make (recommended)
```bash
# Run the email processor
make run

# Run with specific month and year
YEAR=2025 MONTH=5 make run
```

### Direct Python execution

```bash
# Activate the virtual environment
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Run the processor
python process_invoices.py

# Or with environment variables
YEAR=2025 MONTH=5 python process_invoices.py
```

## Makefile Commands

The Makefile provides several useful commands:

```bash
make setup     # Set up the development environment
make install   # Install the package in development mode
make test      # Run tests
make lint      # Run code style checks
make format    # Format the code
make run       # Run the email processor
make clean     # Clean up temporary files
```

## Output Structure

For each processed email attachment, the script will create:
1. The original file (PDF, JPG, etc.)
2. A JSON file with the same base name containing:
   - Original filename
   - Path to the saved file
   - Extracted text (if any)
   - Processing timestamp
   - File size and type

## Security Notes

- Never commit your `.env` file to version control
- The `.env.example` file is versioned, but the actual `.env` is in `.gitignore`
- Use app-specific passwords instead of your main email password
- The script only processes emails from the specified month
- Original files are preserved in their original format
- The virtual environment directory (`venv/`) is also in `.gitignore`

## Troubleshooting

- If you get authentication errors, check your email credentials and ensure IMAP access is enabled
- For OCR errors, verify that Tesseract is installed and in your system PATH
- Check the console output for detailed error messages

## License

This project is licensed under the MIT License - see the LICENSE file for details.
