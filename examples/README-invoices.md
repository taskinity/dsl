# Invoice Processors with Taskinity DSL

This example demonstrates how to use the Taskinity DSL to process both email and web invoices in a containerized environment.

## Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Make (optional)

## Configuration

1. **Email Invoices**

   - Copy the example environment file:
     ```bash
     cp examples/email-invoices/.env.example examples/email-invoices/.env
     ```
   - Update the `.env` file with your email server credentials and settings

2. **Web Invoices**
   - Copy the example environment file:
     ```bash
     cp examples/web-invoices/.env.example examples/web-invoices/.env
     ```
   - Update the `.env` file with your provider credentials (AWS, GCP, Azure, etc.)

## Running with Docker Compose

1. Build and start the services:

   ```bash
   docker-compose -f examples/docker-compose.yml up -d --build
   ```

2. View logs for all services:

   ```bash
   docker-compose -f examples/docker-compose.yml logs -f
   ```

3. View logs for a specific service:

   ```bash
   docker-compose -f examples/docker-compose.yml logs -f email-processor
   docker-compose -f examples/docker-compose.yml logs -f web-processor
   ```

4. Stop the services:
   ```bash
   docker-compose -f examples/docker-compose.yml down
   ```

## Running Locally (Development)

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   pip install -r examples/email-invoices/requirements.txt
   pip install -r examples/web-invoices/requirements.txt
   ```

2. Run the email invoice processor:

   ```bash
   cd examples/email-invoices
   python -m taskinity.runner --config process_invoices.yaml
   ```

3. Run the web invoice processor:
   ```bash
   cd examples/web-invoices
   python -m taskinity.runner --config process_web_invoices.yaml
   ```

## Configuration Files

### Email Invoices (`process_invoices.yaml`)

- **Source**: IMAP server
- **Processors**:
  - Filter emails by date
  - Extract attachments
  - Process PDFs with OCR
- **Output**: JSON files and email notifications

### Web Invoices (`process_web_invoices.yaml`)

- **Providers**: AWS, Google Cloud, Azure
- **Processors**:
  - Download invoices from each provider
  - Process and aggregate data
  - Generate reports
- **Output**: JSON reports and email notifications

## Directory Structure

```
examples/
├── email-invoices/
│   ├── .env.example
│   ├── process_invoices.yaml
│   └── requirements.txt
├── web-invoices/
│   ├── .env.example
│   ├── process_web_invoices.yaml
│   └── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Troubleshooting

1. **Missing Dependencies**

   - Ensure all Python dependencies are installed
   - Check that system dependencies (Tesseract, Poppler) are installed in the container

2. **Configuration Issues**

   - Verify all required environment variables are set in `.env` files
   - Check file permissions for mounted volumes

3. **Logs**
   - Logs are stored in the `logs/` directory
   - Set `LOG_LEVEL=DEBUG` for more verbose logging

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
