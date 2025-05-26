to:
  - "email://{{SMTP_SERVER}}:{{SMTP_PORT}}?user={{SMTP_USER}}&password={{SMTP_PASS}}&to={{SECURITY_EMAIL}}"
  - "http://{{WEBHOOK_URL}}/security-alert"
  - "mqtt://{{MQTT_BROKER}}:1883/alerts/security"
  - "log://security_alerts.log"