# Validate configuration
camel-router validate -c config.yaml

# Check what would be executed
camel-router run -c config.yaml --dry-run

# Run with verbose logging
camel-router run -c config.yaml --verbose