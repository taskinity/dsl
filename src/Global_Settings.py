settings:
  max_concurrent_routes: 10       # Maximum routes running simultaneously
  default_timeout: 30             # Default processor timeout (seconds)
  log_level: "info"               # Logging level (debug, info, warning, error)
  metrics_enabled: true           # Enable Prometheus metrics
  health_check_port: 8080         # Health check HTTP port
  frame_skip_ratio: 3             # Skip video frames for performance
  max_memory_usage: "2GB"         # Maximum memory usage