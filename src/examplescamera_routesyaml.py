# Advanced Camera Processing Routes
# Demonstrates multi-stage processing with different languages

routes:
  - name: "advanced_camera_detection"
    from: "rtsp://{{CAMERA_USER}}:{{CAMERA_PASS}}@{{CAMERA_IP}}/stream1"
    
    processors:
      # Stage 1: Python YOLO object detection
      - type: "external"
        command: "python scripts/detect_objects.py"
        input_format: "json"
        output_format: "json"
        config:
          confidence_threshold: 0.6
          model: "yolov8n.pt"
          target_objects: ["person", "car", "motorcycle", "bicycle"]
          batch_processing: false
      
      # Stage 2: Go-based risk assessment and zone analysis
      - type: "external"
        command: "go run scripts/image_processor.go"
        input_format: "json"
        output_format: "json"
        config:
          zone_mapping: "entrance:critical,parking:medium,garden:low"
          threat_threshold: 0.7
          risk_factors: "time_of_day,object_type,zone,confidence"
      
      # Stage 3: C++ performance optimization and NMS
      - type: "external"
        command: "./bin/cpp_postprocessor"
        input_format: "json"
        output_format: "json"
        config:
          algorithm: "fast_nms"
          nms_threshold: 0.5
          confidence_threshold: 0.7
      
      # Stage 4: Filter only high-risk detections
      - type: "filter"
        condition: "{{threat_level}} in ['high', 'critical']"
      
      # Stage 5: Node.js business rules engine
      - type: "external"
        command: "node scripts/business_rules.js"
        input_format: "json"
        output_format: "json"
        config:
          rules_file: "security_rules.json"
          business_hours: "09:00-17:00"
          escalation_time: 300
      
      # Stage 6: Transform to alert format
      - type: "transform"
        template: |
          🚨 SECURITY ALERT - {{camera_name}}
          
          Threat Level: {{threat_level}} ({{business_priority}})
          Time: {{timestamp}}
          Location: {{zone}} ({{position}})
          
          Detections:
          {{#enhanced_detections}}
          • {{object_type}} - Confidence: {{confidence}}% - Risk: {{risk_score}}
            Recommended Action: {{recommended_action}}
          {{/enhanced_detections}}
          
          Business Context:
          • Business Hours: {{#business_context.is_business_hours}}Yes{{/business_context.is_business_hours}}{{^business_context.is_business_hours}}No{{/business_context.is_business_hours}}
          • Zone Risk: {{business_context.zone_risk_level}}
          • Immediate Response Required: {{business_context.requires_immediate_response}}
    
    to:
      - "email://{{SMTP_SERVER}}:{{SMTP_PORT}}?user={{SMTP_USER}}&password={{SMTP_PASS}}&to={{SECURITY_EMAIL}}"
      - "http://{{SECURITY_WEBHOOK}}/critical-alert"
      - "mqtt://{{MQTT_BROKER}}:1883/security/alerts/{{CAMERA_NAME}}"
      - "log://logs/security_{{CAMERA_NAME}}.log"

  - name: "camera_health_monitoring"
    from: "timer://2m"
    
    processors:
      - type: "external"
        command: "python scripts/camera_health_check.py"
        config:
          camera_endpoints: "{{CAMERA_HEALTH_ENDPOINTS}}"
          timeout: 10
          expected_fps: 25
      
      - type: "filter"
        condition: "{{status}} != 'healthy'"
    
    to: "email://{{SMTP_SERVER}}:{{SMTP_PORT}}?user={{SMTP_USER}}&password={{SMTP_PASS}}&to={{ADMIN_EMAIL}}"

  - name: "motion_detection_backup"
    from: "rtsp://{{BACKUP_CAMERA_USER}}:{{BACKUP_CAMERA_PASS}}@{{BACKUP_CAMERA_IP}}/stream1"
    
    processors:
      - type: "external"
        command: "python scripts/motion_detector.py"
        config:
          sensitivity: 0.3
          min_area: 5000
          background_subtraction: true
      
      - type: "aggregate"
        strategy: "collect"
        timeout: "30s"
        max_size: 5
      
      - type: "transform"
        template: "Motion detected on backup camera: {{count}} events in last 30s"
    
    to: "log://logs/motion_backup.log"

env_vars:
  - CAMERA_USER
  - CAMERA_PASS
  - CAMERA_IP
  - CAMERA_NAME
  - BACKUP_CAMERA_USER
  - BACKUP_CAMERA_PASS
  - BACKUP_CAMERA_IP
  - SMTP_SERVER
  - SMTP_PORT
  - SMTP_USER
  - SMTP_PASS
  - SECURITY_EMAIL
  - ADMIN_EMAIL
  - SECURITY_WEBHOOK
  - MQTT_BROKER
  - CAMERA_HEALTH_ENDPOINTS

settings:
  max_concurrent_routes: 5
  default_timeout: 60
  log_level: "info"
  metrics_enabled: true
  health_check_port: 8080
  frame_skip_ratio: 3
  max_memory_usage: "2GB"