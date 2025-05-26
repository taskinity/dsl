# Test configuration for unit tests
routes:
  - name: "test_timer_route"
    from: "timer://1s"
    processors:
      - type: "transform"
        template: "Timer event at {{timestamp}}"
    to: "log://test_timer.log"

  - name: "test_filter_route"
    from: "timer://2s"
    processors:
      - type: "filter"
        condition: "{{value}} > 10"
      - type: "transform"
        template: "Filtered value: {{value}}"
    to: "log://test_filter.log"

  - name: "test_external_route"
    from: "timer://5s"
    processors:
      - type: "external"
        command: "echo '{\"processed\": true}'"
        input_format: "json"
        output_format: "json"
    to: "log://test_external.log"

  - name: "test_aggregate_route"
    from: "timer://0.5s"
    processors:
      - type: "aggregate"
        strategy: "collect"
        timeout: "3s"
        max_size: 5
    to: "log://test_aggregate.log"

env_vars:
  - TEST_VAR

settings:
  max_concurrent_routes: 2
  default_timeout: 30
  log_level: "debug"