.PHONY: help deploy update backup logs monitor clean

# Variables
INVENTORY = ansible/inventory/hosts.ini
PLAYBOOK = ansible/site.yml
VAULT_PASSWORD_FILE = .vault_pass

# Colors
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)

## Help
help: ## Show this help
	@echo ''
	@echo 'Usage:'
	@echo '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  ${YELLOW}%-20s${GREEN}%s${RESET}\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

## Setup
setup: ## Install required dependencies
	@echo "${YELLOW}Installing dependencies...${RESET}"
	sudo apt-get update
	sudo apt-get install -y \
		ansible \
		python3-pip \
		python3-venv \
		git \
		curl \
		jq

## Deployment
deploy: ## Deploy the entire stack
	@echo "${YELLOW}Deploying edge computing stack...${RESET}"
	ansible-playbook -i $(INVENTORY) $(PLAYBOOK) --tags deploy

## Updates
update: ## Update all nodes
	@echo "${YELLOW}Updating all nodes...${RESET}"
	ansible-playbook -i $(INVENTORY) $(PLAYBOOK) --tags update

## Security
secure: ## Apply security hardening
	@echo "${YELLOW}Applying security hardening...${RESET}"
	ansible-playbook -i $(INVENTORY) $(PLAYBOOK) --tags security

## Backup
backup: ## Backup configurations
	@echo "${YELLOW}Creating backup...${RESET}"
	mkdir -p backups/$(shell date +%Y%m%d)
	ansible-playbook -i $(INVENTORY) $(PLAYBOOK) --tags backup \
		-e "backup_dest=backups/$(shell date +%Y%m%d)"

## Monitoring
monitor: ## Show cluster status
	@echo "${YELLOW}Cluster status:${RESET}"
	ansible -i $(INVENTORY) all -m ping

logs: ## View logs
	@echo "${YELLOW}Viewing logs...${RESET}"
	ansible-playbook -i $(INVENTORY) $(PLAYBOOK) --tags logs

## Maintenance
clean: ## Clean up temporary files
	@echo "${YELLOW}Cleaning up...${RESET}"
	rm -rf __pycache__ *.retry

## Secrets
encrypt: ## Encrypt secrets
	@echo "${YELLOW}Encrypting secrets...${RESET}"
	ansible-vault encrypt \
		--vault-password-file $(VAULT_PASSWORD_FILE) \
		ansible/group_vars/all/vault.yml

decrypt: ## Decrypt secrets
	@echo "${YELLOW}Decrypting secrets...${RESET}"
	ansible-vault decrypt \
		--vault-password-file $(VAULT_PASSWORD_FILE) \
		ansible/group_vars/all/vault.yml

## Development
venv: ## Create Python virtual environment
	@echo "${YELLOW}Creating virtual environment...${RESET}"
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

requirements: ## Update requirements
	@echo "${YELLOW}Updating requirements...${RESET}"
	. venv/bin/activate && pip freeze > requirements.txt
