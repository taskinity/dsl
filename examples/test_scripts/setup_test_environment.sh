#!/bin/bash

# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Create necessary directories
mkdir -p ./output/email
mkdir -p ./logs/email
mkdir -p ./config

# Create test emails directory
TEST_EMAILS_DIR="./test_emails"
mkdir -p "$TEST_EMAILS_DIR"

# Create a test .env file if it doesn't exist
if [ ! -f "./examples/email-invoices/.env" ]; then
    cat > "./examples/email-invoices/.env" <<EOL
# Email Server Configuration
EMAIL_SERVER=localhost
EMAIL_PORT=1143
EMAIL_USER=test@example.com
EMAIL_PASSWORD=testpass
EMAIL_FOLDER=INBOX

# Processing Settings
PROCESSED_FOLDER=Processed
ERROR_FOLDER=Errors
OUTPUT_DIR=./output/email
LOG_LEVEL=DEBUG

# OCR Settings
TESSERACT_CMD=/usr/bin/tesseract
OCR_LANGUAGES=eng,pol
EOL
    echo -e "${GREEN}Created .env file with test configuration${NC}"
fi

# Create a test process_invoices.yaml if it doesn't exist
if [ ! -f "./examples/email-invoices/process_invoices.yaml" ]; then
    cat > "./examples/email-invoices/process_invoices.yaml" <<EOL
# Email Invoice Processor Configuration

# Email server configuration
email:
  server: "{{EMAIL_SERVER}}"
  port: {{EMAIL_PORT}}
  username: "{{EMAIL_USER}}"
  password: "{{EMAIL_PASSWORD}}"
  folder: "{{EMAIL_FOLDER}}"
  processed_folder: "{{PROCESSED_FOLDER}}"
  error_folder: "{{ERROR_FOLDER}}"

# Processing settings
output_dir: "{{OUTPUT_DIR}}"
log_level: "{{LOG_LEVEL}}"

# File patterns to look for in emails (case insensitive)
file_patterns:
  - '*.pdf'
  - '*.jpg'
  - '*.jpeg'
  - '*.png'
  - '*.tiff'
  - '*.bmp'
EOL
    echo -e "${GREEN}Created process_invoices.yaml configuration${NC}"
fi

# Create a test email with attachment
create_test_email() {
    local email_file="$1"
    local subject="$2"
    local from="$3"
    local to="$4"
    local attachment_path="$5"
    local attachment_name="$(basename "$attachment_path")"
    
    # Create a boundary
    local boundary="$(uuidgen)"
    
    # Create the email with attachment
    {
        # Headers
        echo "From: $from"
        echo "To: $to"
        echo "Subject: $subject"
        echo "MIME-Version: 1.0"
        echo "Content-Type: multipart/mixed; boundary=\"$boundary\""
        echo ""
        
        # Message body
        echo "--$boundary"
        echo "Content-Type: text/plain; charset=utf-8"
        echo ""
        echo "This is a test email with an attachment."
        echo ""
        
        # Attachment
        echo "--$boundary"
        echo "Content-Type: application/octet-stream; name=\"$attachment_name\""
        echo "Content-Transfer-Encoding: base64"
        echo "Content-Disposition: attachment; filename=\"$attachment_name\""
        echo ""
        base64 "$attachment_path"
        echo "--$boundary--"
    } > "$email_file"
    
    echo -e "${GREEN}Created test email: $email_file${NC}"
}

# Create a simple PDF invoice for testing
echo "Creating test PDF invoice..."
cat > /tmp/test_invoice.tex <<EOL
\documentclass{article}
\begin{document}
\begin{center}
    \Large\textbf{INVOICE}
    \vspace{1cm}
    
    \begin{tabular}{ll}
        \textbf{Invoice Number:} & INV-2023-001 \\
        \textbf{Date:} & $(date +"%Y-%m-%d") \\
        \textbf{Amount:} & \$1,234.56 \\
        \textbf{Description:} & Test Invoice \\
    \end{tabular}
\end{center}
\end{document}
EOL

# Compile the LaTeX document to PDF
if command -v pdflatex &> /dev/null; then
    (cd /tmp && pdflatex -interaction=nonstopmode test_invoice.tex >/dev/null)
    if [ -f "/tmp/test_invoice.pdf" ]; then
        cp /tmp/test_invoice.pdf "./$TEST_EMAILS_DIR/invoice_$(date +%Y%m%d).pdf"
        echo -e "${GREEN}Created test PDF invoice${NC}"
    else
        echo "Warning: Failed to create test PDF invoice, pdflatex might not be installed"
    fi
else
    echo "Warning: pdflatex not found, skipping PDF invoice creation"
    # Create a simple text file as fallback
    echo "INVOICE" > "./$TEST_EMAILS_DIR/invoice_$(date +%Y%m%d).txt"
    echo "Number: INV-2023-001" >> "./$TEST_EMAILS_DIR/invoice_$(date +%Y%m%d).txt"
    echo "Date: $(date +"%Y-%m-%d")" >> "./$TEST_EMAILS_DIR/invoice_$(date +%Y%m%d).txt"
    echo "Amount: \$1,234.56" >> "./$TEST_EMAILS_DIR/invoice_$(date +%Y%m%d).txt"
    echo "Description: Test Invoice" >> "./$TEST_EMAILS_DIR/invoice_$(date +%Y%m%d).txt"
fi

# Create test emails
create_test_email \
    "./$TEST_EMAILS_DIR/test_email_1.eml" \
    "Test Invoice $(date +%Y%m%d)" \
    "vendor@example.com" \
    "accounting@example.com" \
    "./$TEST_EMAILS_DIR/invoice_$(date +%Y%m%d).pdf"

# Create a second test email with a different vendor
create_test_email \
    "./$TEST_EMAILS_DIR/test_email_2.eml" \
    "Monthly Subscription $(date +%B %Y)" \
    "billing@service.com" \
    "accounting@example.com" \
    "./$TEST_EMAILS_DIR/invoice_$(date +%Y%m%d).pdf"

echo -e "\n${GREEN}Test environment setup complete!${NC}"
echo -e "Test emails are available in: $TEST_EMAILS_DIR/"
echo -e "To start the email server, run: docker-compose up -d mailserver"
echo -e "To load test emails, run: ./test_scripts/load_test_emails.sh"
