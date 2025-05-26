# Global settings
settings:
  max_concurrent_routes: 10
  default_timeout: 30
  log_level: "info"

# Route definitions
routes:
  - name: "route_1"
    from: "source_uri"
    processors:
      - type: "processor_type"
        config: {}
    to: "destination_uri"

# Required environment variables
env_vars:
  - VARIABLE_NAME