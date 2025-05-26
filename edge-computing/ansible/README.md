# Edge Computing Ansible Playbooks

This directory contains Ansible playbooks and roles for setting up and managing an edge computing infrastructure.

## Directory Structure

```
ansible/
├── group_vars/
│   └── all/
│       ├── vars.yml      # Common variables
│       └── vault.yml     # Encrypted sensitive data
├── inventory/
│   └── hosts.ini      # Inventory file with hosts and groups
├── roles/
│   ├── backup/        # Backup configuration
│   ├── common/         # Common system setup
│   ├── docker/         # Docker installation
│   ├── gitea/          # Gitea Git service
│   ├── monitoring/     # Monitoring stack (Telegraf, InfluxDB)
│   ├── node_red/       # Node-RED installation
│   ├── portainer/      # Portainer container management
│   └── security/       # Security hardening
└── site.yml            # Main playbook
```

## Prerequisites

1. Ansible installed on your control machine
2. SSH access to all nodes
3. Python 3.6+ on all nodes
4. Sudo privileges on all nodes

## Usage

1. Edit the inventory file (`inventory/hosts.ini`) with your node information
2. Update variables in `group_vars/all/vars.yml`
3. Encrypt sensitive data in `group_vars/all/vault.yml` using Ansible Vault:

   ```bash
   ansible-vault encrypt group_vars/all/vault.yml
   ```

4. Run the playbook:
   ```bash
   ansible-playbook -i inventory/hosts.ini site.yml --ask-vault-pass
   ```

## Available Tags

Run specific parts of the playbook using tags:

- `common`: Basic system setup
- `docker`: Docker installation
- `portainer`: Portainer deployment
- `gitea`: Gitea deployment
- `node-red`: Node-RED deployment
- `monitoring`: Monitoring stack
- `security`: Security hardening
- `backup`: Backup configuration
- `deploy`: All deployment roles

Example:

```bash
ansible-playbook -i inventory/hosts.ini site.yml --tags "docker,portainer" --ask-vault-pass
```

## Security Notes

- Always encrypt sensitive data using Ansible Vault
- Review and adjust firewall rules in the security role
- Regularly update your playbooks and roles
- Use SSH keys for authentication
- Limit SSH access to trusted networks

## Backup and Recovery

Backups are configured to run automatically:

- Daily backups with 7-day retention
- Weekly backups with 30-day retention
- Monthly backups with 90-day retention

To restore from backup, use the appropriate backup file and restore it to the target directory.
