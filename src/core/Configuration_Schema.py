routes:
  - name: "route_name"              # Required: Unique route identifier
    from: "source_uri"              # Required: Source URI
    processors:                     # Optional: Processing pipeline
      - type: "processor_type"      # Required: Processor type
        config: {}                  # Optional: Processor-specific config
    to: ["destination_uri"]         # Required: Destination URI(s)