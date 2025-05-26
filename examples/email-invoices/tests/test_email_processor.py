"""
Tests for the email invoice processor.
"""

import unittest
from unittest.mock import patch, MagicMock

# Import the module to test
from email_processor import EmailProcessor

class TestEmailProcessor(unittest.TestCase):
    """Test cases for the EmailProcessor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "email": {
                "server": "imap.example.com",
                "port": 993,
                "username": "test@example.com",
                "password": "testpass",
                "folder": "INBOX"
            },
            "output_dir": "/tmp/invoices",
            "processed_folder": "Processed",
            "error_folder": "Errors"
        }
        self.processor = EmailProcessor(self.config)

    def test_initialization(self):
        """Test that the processor initializes correctly."""
        self.assertEqual(self.processor.config, self.config)
        self.assertIsNone(self.processor.mail)

    @patch('imaplib.IMAP4_SSL')
    def test_connect_email(self, mock_imap):
        """Test connecting to email server."""
        mock_imap.return_value = MagicMock()
        self.processor._connect_email()
        self.assertIsNotNone(self.processor.mail)
        mock_imap.assert_called_once_with(
            self.config["email"]["server"],
            self.config["email"]["port"]
        )

    def test_process_emails_no_connection(self):
        """Test processing emails when not connected."""
        with self.assertRaises(RuntimeError):
            self.processor.process_emails()

    # Add more test methods as needed

if __name__ == "__main__":
    unittest.main()
