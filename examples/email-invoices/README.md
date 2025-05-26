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

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Copy the example config file:
   ```bash
   cp config/config.json.example config/config.json
   ```

2. Edit `config/config.json` with your email credentials and settings:
   - `email`: Your email address
   - `password`: Your email password or app-specific password
   - `imap_server`: IMAP server address (e.g., imap.gmail.com)
   - `imap_port`: IMAP port (usually 993 for SSL)
   - `output_dir`: Directory to save processed files
   - `year`: Year to process (e.g., 2025)
   - `month`: Month to process (1-12, e.g., 5 for May)

## Usage

Run the processor:
```bash
python process_invoices.py
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

- Never commit your email credentials to version control
- Consider using environment variables or a secrets manager in production
- The script only processes emails from the specified month
- Original files are preserved in their original format

## Troubleshooting

- If you get authentication errors, check your email credentials and ensure IMAP access is enabled
- For OCR errors, verify that Tesseract is installed and in your system PATH
- Check the console output for detailed error messages

## License

This project is licensed under the MIT License - see the LICENSE file for details.
