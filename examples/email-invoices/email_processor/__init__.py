"""
Email Invoice Processor

A package for processing email attachments, particularly invoice PDFs and images,
extracting text using OCR, and saving them in a structured format.
"""

__version__ = "0.1.0"

from .process_invoices import EmailProcessor  # noqa: F401

__all__ = ["EmailProcessor"]
