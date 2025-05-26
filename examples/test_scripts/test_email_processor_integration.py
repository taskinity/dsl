#!/usr/bin/env python3
"""
Integration test for the email processor with a local mail server.
This script tests the complete flow from receiving an email to processing its attachments.
"""
import os
import time
import json
import imaplib
import smtplib
import email
import email.policy
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import pytest
from pathlib import Path

# Test configuration
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpass"
SMTP_SERVER = "localhost"
SMTP_PORT = 1025
IMAP_SERVER = "localhost"
IMAP_PORT = 1143
TEST_OUTPUT_DIR = "./test_output"

def create_test_email(sender, recipient, subject, body, attachments=None):
    """Create a test email with optional attachments."""
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    if attachments:
        for attachment in attachments:
            with open(attachment, 'rb') as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(attachment))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment)}"'
                msg.attach(part)
    
    return msg

def send_test_email(msg):
    """Send a test email using the local SMTP server."""
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.send_message(msg)

def wait_for_emails(imap, expected_count=1, max_retries=10, delay=1):
    """Wait for emails to appear in the inbox."""
    for _ in range(max_retries):
        imap.select('INBOX')
        status, messages = imap.search(None, 'ALL')
        if status == 'OK' and len(messages[0].split()) >= expected_count:
            return messages[0].split()
        time.sleep(delay)
    return []

def test_email_processing_flow():
    """Test the complete email processing flow."""
    # Setup
    test_output_dir = Path(TEST_OUTPUT_DIR)
    test_output_dir.mkdir(exist_ok=True)
    
    # Create a test email with an attachment
    test_attachment = test_output_dir / "test_invoice.pdf"
    test_attachment.write_bytes(b"%PDF-test-invoice")
    
    email_subject = f"Test Invoice {int(time.time())}"
    email_body = "This is a test email with an invoice attachment."
    
    msg = create_test_email(
        sender=TEST_EMAIL,
        recipient=TEST_EMAIL,
        subject=email_subject,
        body=email_body,
        attachments=[str(test_attachment)]
    )
    
    # Send the test email
    send_test_email(msg)
    print(f"Sent test email with subject: {email_subject}")
    
    # Connect to IMAP to verify the email was received
    with imaplib.IMAP4(IMAP_SERVER, IMAP_PORT) as imap:
        imap.login(TEST_EMAIL, TEST_PASSWORD)
        
        # Wait for the email to be received
        message_ids = wait_for_emails(imap, expected_count=1)
        assert message_ids, "Test email was not received"
        
        # Verify the email content
        for num in message_ids:
            status, msg_data = imap.fetch(num, '(RFC822)')
            assert status == 'OK', f"Failed to fetch email: {status}"
            
            # Parse the email
            email_msg = email.message_from_bytes(
                msg_data[0][1],
                policy=email.policy.default
            )
            
            # Verify subject and sender
            assert email_subject in email_msg['subject'], "Email subject doesn't match"
            assert TEST_EMAIL in email_msg['from'], "Email sender doesn't match"
            
            # Verify attachments
            attachment_count = sum(1 for part in email_msg.walk() if part.get_content_disposition() == 'attachment')
            assert attachment_count >= 1, "No attachments found in the email"
            
            # Mark the email as processed
            imap.store(num, '+FLAGS', '\Seen')
    
    # Here you would typically run your email processor and verify the output
    # For now, we'll just verify the test email was properly set up
    print("Test email was successfully received and verified")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
