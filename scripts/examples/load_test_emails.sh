#!/bin/bash

# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if swaks is installed
if ! command -v swaks &> /dev/null; then
    echo -e "${RED}Error: swaks is required but not installed.${NC}"
    echo "Install it with your package manager, for example:"
    echo "  - macOS: brew install swaks"
    echo "  - Ubuntu/Debian: sudo apt-get install swaks"
    echo "  - Fedora: sudo dnf install swaks"
    exit 1
fi

# Load environment variables from .env file
if [ -f "./examples/email-invoices/.env" ]; then
    export $(grep -v '^#' ./examples/email-invoices/.env | xargs)
else
    echo -e "${RED}Error: .env file not found in ./examples/email-invoices/${NC}"
    echo "Please run ./test_scripts/setup_test_environment.sh first"
    exit 1
fi

# Default values
MAIL_SERVER=${EMAIL_SERVER:-localhost}
MAIL_PORT=${EMAIL_PORT:-1143}
MAIL_FROM="test@example.com"
MAIL_TO=${EMAIL_USER:-}
MAIL_USER=${EMAIL_USER}
MAIL_PASS=${EMAIL_PASSWORD}
TEST_EMAILS_DIR="./test_emails"

# Check if test emails directory exists
if [ ! -d "$TEST_EMAILS_DIR" ]; then
    echo -e "${RED}Error: Test emails directory not found: $TEST_EMAILS_DIR${NC}"
    echo "Please run ./test_scripts/setup_test_environment.sh first"
    exit 1
fi

# Function to send a test email
send_test_email() {
    local email_file="$1"
    local email_subject="$(grep -i '^Subject:' "$email_file" | sed 's/^Subject: //' | tr -d '\r')"
    
    if [ -z "$email_subject" ]; then
        email_subject="Test email $(date +"%Y-%m-%d %H:%M:%S")"
    fi
    
    echo -e "${GREEN}Sending email: $email_subject${NC}"
    
    # Extract the message body (text/plain part)
    local boundary=$(grep -m 1 '^Content-Type: multipart/mixed; boundary=' "$email_file" | sed 's/.*boundary="\([^"]*\)".*/\1/')
    local body=""
    
    if [ -n "$boundary" ]; then
        # Extract text/plain part
        body=$(sed -n "/--$boundary/,/--$boundary/{
            /^--$boundary/d
            /^Content-Type: text\/plain;/,/^$/{
                /^Content-Type: text\/plain;/d
                /^$/d
                p
            }
        }" "$email_file")
    fi
    
    if [ -z "$body" ]; then
        body="This is a test email with an attachment."
    fi
    
    # Send the email using swaks
    swaks \
        --server "$MAIL_SERVER:$MAIL_PORT" \
        --from "$MAIL_FROM" \
        --to "$MAIL_TO" \
        --h-Subject: "$email_subject" \
        --body "$body" \
        --attach "$email_file" \
        --auth-user "$MAIL_USER" \
        --auth-password "$MAIL_PASS" \
        --auth LOGIN \
        --tls-on-connect \
        --quit-after FROM
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Successfully sent: $email_subject${NC}"
    else
        echo -e "${RED}Failed to send: $email_subject${NC}"
    fi
    
    # Add a small delay between emails
    sleep 1
}

# Main script
echo -e "${GREEN}Loading test emails to $MAIL_SERVER:$MAIL_PORT...${NC}"

# Check if there are any .eml files in the test emails directory
if ! ls "$TEST_EMAILS_DIR"/*.eml 1> /dev/null 2>&1; then
    echo -e "${RED}No .eml files found in $TEST_EMAILS_DIR/${NC}"
    echo "Please run ./test_scripts/setup_test_environment.sh first"
    exit 1
fi

# Send each test email
for email_file in "$TEST_EMAILS_DIR"/*.eml; do
    send_test_email "$email_file"
done

echo -e "\n${GREEN}All test emails have been sent!${NC}"
echo "You can now run the email processor to process these emails."
echo -e "Run: ${GREEN}make run${NC} or ${GREEN}docker-compose up -d email-processor${NC}"
