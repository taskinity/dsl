processors:
  - type: "external"
    command: "python scripts/detect_objects.py"
    input_format: "json"
    output_format: "json"
    timeout: 30
    async: false
    config:
      confidence_threshold: 0.6
      model: "yolov8n.pt"