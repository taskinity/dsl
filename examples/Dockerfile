# Use Python 3.9 as the base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies for OCR and image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-pol \
    poppler-utils \
    ghostscript \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements files
COPY requirements.txt .
COPY examples/email-invoices/requirements.txt ./email-requirements.txt
COPY examples/web-invoices/requirements.txt ./web-requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r email-requirements.txt \
    && pip install --no-cache.txt -r web-requirements.txt

# Copy application code
COPY . .

# Create directories for logs and output
RUN mkdir -p /app/logs \
    && mkdir -p /app/output

# Copy configuration files
COPY examples/email-invoices/.env.example /app/examples/email-invoices/.env
COPY examples/web-invoices/.env.example /app/examples/web-invoices/.env
COPY examples/email-invoices/process_invoices.yaml /app/config/email_invoices.yaml
COPY examples/web-invoices/process_web_invoices.yaml /app/config/web_invoices.yaml

# Set environment variables for configuration
ENV EMAIL_CONFIG=/app/config/email_invoices.yaml \
    WEB_CONFIG=/app/config/web_invoices.yaml \
    LOG_DIR=/app/logs \
    OUTPUT_DIR=/app/output

# Create a non-root user and switch to it
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=2)" || exit 1

# Default command (can be overridden)
CMD ["python", "-m", "taskinity.cli", "--config", "/app/config/email_invoices.yaml"]
