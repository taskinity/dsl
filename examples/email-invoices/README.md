# Email Invoice Processor

This is an email invoice processor that demonstrates how to use the Taskinity DSL for processing email attachments with local OCR processing. The processor can be run both locally and in Docker containers.

## Features

- Fetches emails from IMAP server
- Processes email attachments (PDF, JPG, PNG, TIFF, BMP)
- Local OCR processing with Tesseract
- Extracts invoice data to structured format
- Configurable through YAML and environment variables
- Docker support for easy setup and testing
- Test environment with sample emails

## Prerequisites

### For Local Development

- Python 3.8+
- Tesseract OCR
- Poppler Utils (for PDF processing)
- Required Python packages (see `requirements.txt`)

### For Docker (Recommended)

- Docker 20.10+
- Docker Compose 2.0+

## Quick Start with Docker

The easiest way to get started is using Docker Compose, which will set up everything you need, including a test mail server:

```bash
# Navigate to the project root
cd /path/to/taskinity-dsl

# Start all services in detached mode
docker-compose -f examples/docker-compose.yml up -d

# View the MailHog web interface at http://localhost:8025
# The email processor will be running and processing emails

# Load test emails into the mail server
./test_scripts/load_test_emails.sh

# View the email processor logs
docker logs -f email-invoice-processor
```

### Services

- **MailHog**: Test SMTP server with web UI (http://localhost:8025)
- **Email Processor**: Processes incoming emails and extracts invoice data
- **Taskinity DSL**: Main application service

## Development Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/taskinity/taskinity-dsl.git
   cd taskinity-dsl/examples/email-invoices
   ```

2. Set up the development environment:

   ```bash
   # Install system dependencies (Ubuntu/Debian)
   sudo apt-get update && sudo apt-get install -y \
       tesseract-ocr tesseract-ocr-eng tesseract-ocr-pol \
       poppler-utils ghostscript swaks jq

   # Or using the Makefile:
   make install-deps
   ```

3. Set up the Python environment:

   ```bash
   # Create and activate a virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install the package in development mode
   pip install -e .

   # Install development dependencies
   pip install -r requirements-dev.txt
   ```

4. Set up the test environment:

   ```bash
   # Create necessary directories
   mkdir -p output/email logs/email

   # Set up test environment and load test emails
   ./test_scripts/setup_test_environment.sh
   ```

## Configuration

### Environment Variables

Create a `.env` file in the `email-invoices` directory with the following variables:

```ini
# Email Server Configuration
# For local development with MailHog
EMAIL_SERVER=localhost
EMAIL_PORT=1025
EMAIL_USER=test@example.com
EMAIL_PASSWORD=testpass
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
  port: { { EMAIL_PORT|int } }
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

### Running Tests

```bash
# Run all tests
make test

# Run a specific test file
pytest tests/test_email_processor.py -v

# Run with coverage report
pytest --cov=email_processor tests/

# Run integration tests
pytest tests/integration/ -v
```

### Testing with Docker

1. Start the test environment:

   ```bash
   docker-compose -f examples/docker-compose.yml up -d
   ```

2. Load test emails:

   ```bash
   ./test_scripts/load_test_emails.sh
   ```

3. View logs:

   ```bash
   docker logs -f email-invoice-processor
   ```

4. Access MailHog web interface:
   - Open http://localhost:8025 in your browser
   - View processed emails and test results

### Linting and Formatting

```bash
# Run linter
make lint

# Format code
make format

# Check types
make typecheck
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
version: "3.8"
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
