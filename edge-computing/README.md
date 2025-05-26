# Edge Computing Infrastructure

This project sets up a complete edge computing infrastructure using Raspberry Pi nodes managed by a central control plane.

## Architecture

```
[Desktop PC (Control Plane)]
       |
       |-- [Raspberry Pi Worker 1]
       |-- [Raspberry Pi Worker 2]
       |-- [Raspberry Pi Worker N]
```

## Prerequisites

- Ansible 2.9+
- Python 3.8+
- Docker & Docker Compose
- SSH access to all nodes

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd edge-computing
   ```

2. **Configure inventory**
   Edit `ansible/inventory/hosts.ini` with your node details

3. **Deploy the stack**
   ```bash
   make deploy
   ```

## Directory Structure

```
.
├── ansible/               # Ansible playbooks and roles
├── config/               # Configuration files
│   ├── telegraf/        # Telegraf configurations
│   └── node-red/        # Node-RED flows
├── docs/                # Documentation
├── scripts/             # Utility scripts
└── .github/workflows/   # GitHub Actions workflows
```

## Accessing Services

| Service     | URL                           | Default Credentials     |
|-------------|-------------------------------|-------------------------|
| Portainer   | http://<node-ip>:9000         | admin / changeme        |
| Gitea      | http://<node-ip>:3000         | admin / admin@local     |
| Node-RED   | http://<node-ip>:1880         | -                      |
| InfluxDB   | http://<node-ip>:8086         | admin / admin123       |


## Security

- SSH key-based authentication only
- UFW firewall enabled by default
- Fail2ban for intrusion prevention
- Automatic security updates

## Maintenance

- Update all nodes: `make update`
- Backup configurations: `make backup`
- View logs: `make logs`

## License

MIT License - see [LICENSE](LICENSE) for details.
