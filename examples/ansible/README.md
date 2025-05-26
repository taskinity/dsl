# Ansible Playbook for Taskinity Invoice Processors

This directory contains Ansible playbooks for setting up and testing the Taskinity email and web invoice processors.

## Prerequisites

- Ansible 2.9+
- Python 3.8+
- Ubuntu/Debian or compatible system (for system package installation)

## Directory Structure

```
ansible/
├── playbook.yml           # Main playbook
├── inventory/             # Inventory files
│   └── localhost.ini      # Local inventory
├── group_vars/            # Group variables
│   └── all.yml            # Variables for all hosts
└── templates/             # Configuration templates
    ├── email-invoices/    # Email processor templates
    │   └── .env.j2       # Email processor environment template
    └── web-invoices/      # Web processor templates
        └── .env.j2       # Web processor environment template
```

## Quick Start

1. Install Ansible:

   ```bash
   sudo apt update
   sudo apt install -y ansible
   ```

2. Run the playbook:
   ```bash
   cd /path/to/taskinity-dsl/examples/ansible
   ansible-playbook -i inventory/localhost.ini playbook.yml
   ```

## Available Tags

The playbook includes several tags for running specific parts:

- `deps`: Install all dependencies
  - `system`: System packages only
  - `python`: Python packages only
  - `email`: Email processor dependencies
  - `web`: Web processor dependencies
- `venv`: Create virtual environment
- `setup`: Setup directories and files
- `config`: Configure environment files
- `test`: Run tests
  - `email`: Email processor tests
  - `web`: Web processor tests

## Examples

### Install Dependencies Only

```bash
ansible-playbook -i inventory/localhost.ini playbook.yml --tags deps
```

### Run Tests Only

```bash
ansible-playbook -i inventory/localhost.ini playbook.yml --tags test
```

### Configure and Test Email Processor

```bash
ansible-playbook -i inventory/localhost.ini playbook.yml \
  --tags "config,test" \
  --extra-vars "email_user=test@example.com email_password=pass123"
```

## Variables

### Email Processor Variables

| Variable           | Default                  | Description                 |
| ------------------ | ------------------------ | --------------------------- |
| `email_server`     | `imap.example.com`       | IMAP server address         |
| `email_port`       | `993`                    | IMAP server port            |
| `email_user`       | `your-email@example.com` | Email username              |
| `email_password`   | `your-password`          | Email password              |
| `email_folder`     | `INBOX`                  | Email folder to process     |
| `processed_folder` | `Processed`              | Folder for processed emails |
| `error_folder`     | `Errors`                 | Folder for error emails     |
| `output_dir`       | `./output`               | Output directory            |
| `log_level`        | `INFO`                   | Logging level               |
| `tesseract_cmd`    | `/usr/bin/tesseract`     | Path to Tesseract OCR       |
| `ocr_languages`    | `eng,pol`                | OCR languages               |

### Web Processor Variables

| Variable                         | Default                     | Description             |
| -------------------------------- | --------------------------- | ----------------------- |
| `aws_access_key_id`              | `your_access_key`           | AWS Access Key ID       |
| `aws_secret_access_key`          | `your_secret_key`           | AWS Secret Access Key   |
| `aws_region`                     | `us-east-1`                 | AWS Region              |
| `google_application_credentials` | `/path/to/credentials.json` | Path to GCP credentials |
| `azure_subscription_id`          | `your_subscription_id`      | Azure Subscription ID   |
| `azure_tenant_id`                | `your_tenant_id`            | Azure Tenant ID         |
| `azure_client_id`                | `your_client_id`            | Azure Client ID         |
| `azure_client_secret`            | `your_client_secret`        | Azure Client Secret     |
| `output_dir`                     | `./output`                  | Output directory        |
| `log_level`                      | `INFO`                      | Logging level           |

## Testing with Docker

You can also test the processors using Docker:

1. Build the Docker images:

   ```bash
   cd /path/to/taskinity-dsl
   docker-compose -f examples/docker-compose.yml build
   ```

2. Run the tests:
   ```bash
   docker-compose -f examples/docker-compose.yml run --rm email-processor pytest /app/tests/
   docker-compose -f examples/docker-compose.yml run --rm web-processor pytest /app/tests/
   ```

## Troubleshooting

### Common Issues

1. **Permission Denied**

   - Run the playbook with `--become` if you need root privileges
   - Ensure the user has sudo access

2. **Python Dependencies**

   - Make sure Python 3.8+ is installed
   - Check that pip is up to date

3. **Test Failures**
   - Verify all environment variables are set correctly
   - Check the logs in the `logs/` directory

## License

This project is licensed under the MIT License - see the [LICENSE](../../../LICENSE) file for details.
