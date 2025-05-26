# Email Invoice Processor

This is an email invoice processor that demonstrates how to use the Taskinity DSL for processing email attachments with local OCR processing.

## Features

- Fetches emails from IMAP server
- Processes email attachments (PDF, JPG, PNG)
- Local OCR processing with Tesseract
- Extracts invoice data to structured format
- Configurable through YAML and environment variables

## Prerequisites

- Python 3.8+
- Tesseract OCR
- Poppler Utils (for PDF processing)
- Required Python packages (see `requirements.txt`)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/taskinity-dsl.git
   cd taskinity-dsl/examples/email-invoices
   ```

2. Install system dependencies:
   ```bash
   # Ubuntu/Debian
   sudo apt-get update && sudo apt-get install -y \
       tesseract-ocr tesseract-ocr-eng tesseract-ocr-pol \
       poppler-utils ghostscript
   
   # Or using the Makefile:
   make install-deps
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy and configure the environment:
   ```bash
   cp .env.example .env
   # Edit .env with your email settings
   ```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```ini
# Email Server Configuration
EMAIL_SERVER=imap.example.com
EMAIL_PORT=993
EMAIL_USER=your-email@example.com
EMAIL_PASSWORD=your-password
EMAIL_FOLDER=INBOX

# Processing Settings
PROCESSED_FOLDER=Processed
ERROR_FOLDER=Errors
OUTPUT_DIR=./output
LOG_LEVEL=INFO

# OCR Settings
TESSERACT_CMD=/usr/bin/tesseract
OCR_LANGUAGES=eng,pol
```

### YAML Configuration

The main configuration is in `process_invoices.yaml`. Key sections:

```yaml
email:
  server: "{{EMAIL_SERVER}}"
  port: {{EMAIL_PORT|int}}
  username: "{{EMAIL_USER}}"
  password: "{{EMAIL_PASSWORD}}"
  folder: "{{EMAIL_FOLDER|default('INBOX')}}"

processing:
  output_dir: "{{OUTPUT_DIR|default('./output')}}"
  processed_folder: "{{PROCESSED_FOLDER|default('Processed')}}"
  error_folder: "{{ERROR_FOLDER|default('Errors')}}"
  
ocr:
  engine: "tesseract"
  config:
    tesseract_cmd: "{{TESSERACT_CMD|default('tesseract')}}"
    languages: ["eng", "pol"]
```

## Usage

### Command Line

```bash
# Process emails using the DSL
python -m taskinity.runner --config process_invoices.yaml

# Or use the Python script directly
python -m email_processor --config process_invoices.yaml

# Process specific email by ID
python -m email_processor --email-id 12345

# Process emails from a specific date
python -m email_processor --since "2023-01-01"
```

### Makefile Commands

```bash
# Install dependencies
make install

# Run the processor
make run

# Run tests
make test

# Clean up
make clean
```

## Testing

### Unit Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=email_processor tests/
```

### Integration Tests

1. Start a test email server:
   ```bash
   python -m smtpd -n -c DebuggingServer localhost:1025
   ```

2. Run the processor in test mode:
   ```bash
   python -m email_processor --test-mode
   ```

## Logs

Logs are written to the following locations by default:

- Application logs: `logs/email_processor.log`
- Error logs: `logs/errors.log`
- Debug logs: `logs/debug.log` (when LOG_LEVEL=DEBUG)

View logs in real-time:
```bash
tail -f logs/email_processor.log
```

## Docker

### Build and Run

```bash
# Build the image
docker build -t email-processor .

# Run the container
docker run --rm -v $(pwd)/output:/app/output email-processor
```

### Docker Compose

```yaml
version: '3.8'
services:
  email-processor:
    build: .
    volumes:
      - ./output:/app/output
      - ./logs:/app/logs
    environment:
      - EMAIL_SERVER=imap.example.com
      - EMAIL_USER=user@example.com
      - EMAIL_PASSWORD=password
    restart: unless-stopped
```

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify email credentials
   - Check if IMAP access is enabled for your email account
   - For Gmail, you may need to use an App Password

2. **OCR Not Working**
   - Ensure Tesseract is installed and in PATH
   - Verify language packs are installed
   - Check file permissions on input files

3. **PDF Processing Errors**
   - Ensure Poppler Utils is installed
   - Check PDF file integrity

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
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
