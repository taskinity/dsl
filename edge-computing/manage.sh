#!/bin/bash

# Edge Computing Management Script
# Usage: ./manage.sh [command] [options]

set -euo pipefail

# Configuration
ANSIBLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/ansible" && pwd)"
INVENTORY_FILE="${ANSIBLE_DIR}/inventory/hosts.ini"
VAULT_FILE="${ANSIBLE_DIR}/group_vars/all/vault.yml"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Ansible is installed
check_ansible() {
    if ! command -v ansible &> /dev/null; then
        echo -e "${RED}Error: Ansible is not installed. Please install it first.${NC}"
        exit 1
    fi
}

# Run Ansible playbook
run_playbook() {
    local playbook="$1"
    local tags="${2:-}"
    local extra_vars="${3:-}"
    
    local cmd=("ansible-playbook" "-i" "${INVENTORY_FILE}")
    
    if [ -f "${VAULT_FILE}" ]; then
        cmd+=("--ask-vault-pass")
    fi
    
    if [ -n "${tags}" ]; then
        cmd+=("--tags" "${tags}")
    fi
    
    if [ -n "${extra_vars}" ]; then
        cmd+=("--extra-vars" "${extra_vars}")
    fi
    
    cmd+=("${ANSIBLE_DIR}/${playbook}")
    
    echo -e "${YELLOW}Running: ${cmd[*]}${NC}"
    "${cmd[@]}"
}

# Show help
show_help() {
    echo -e "${GREEN}Edge Computing Management Script${NC}"
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  deploy [tags]    Deploy the entire stack or specific components"
    echo "  update [tags]    Update specific components"
    echo "  status           Show status of services"
    echo "  backup           Run backup"
    echo "  encrypt          Encrypt vault file"
    echo "  decrypt          Decrypt vault file"
    echo "  help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy"
    echo "  $0 deploy portainer,node-red"
    echo "  $0 status"
    echo "  $0 encrypt"
}

# Check service status
check_status() {
    echo -e "${YELLOW}Checking service status...${NC}"
    ansible all -i "${INVENTORY_FILE}" -m shell -a "systemctl list-units 'docker*' --no-pager"
    echo -e "\n${YELLOW}Running containers:${NC}"
    ansible all -i "${INVENTORY_FILE}" -m shell -a "docker ps --format '{{.Names}} ({{.Status}})'"
}

# Main script
main() {
    local command="${1:-help}"
    shift
    
    check_ansible
    
    case "${command}" in
        deploy)
            run_playbook "site.yml" "$*"
            ;;
        update)
            run_playbook "site.yml" "$*" "update=true"
            ;;
        status)
            check_status
            ;;
        backup)
            ansible-playbook -i "${INVENTORY_FILE}" "${ANSIBLE_DIR}/site.yml" --tags "backup" --ask-vault-pass
            ;;
        encrypt)
            ansible-vault encrypt "${VAULT_FILE}"
            ;;
        decrypt)
            ansible-vault edit "${VAULT_FILE}"
            ;;
        help|*)
            show_help
            ;;
    esac
}

# Run main function with all arguments
main "$@"
