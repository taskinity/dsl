# IoT Routes Example

This example demonstrates IoT device communication patterns using Taskinity DSL, including MQTT and HTTP endpoints for device communication.

## Prerequisites

- Python 3.8 or higher
- MQTT broker (e.g., Mosquitto)
- Taskinity DSL installed
- Docker (for containerized MQTT broker)

## Example Files

- `iot_routes.yaml` - Main configuration file
- `docker-compose.yml` - MQTT broker setup
- `devices/` - Example device simulators

## Running the Example

### Using Make (Recommended)

```bash
# Start MQTT broker and device simulators
make run-example EXAMPLE=iot

# View logs
make logs-example EXAMPLE=iot

# Stop the example
make stop-example EXAMPLE=iot
```

### Manual Execution

1. Start the MQTT broker:

   ```bash
   docker-compose -f examples/docker-compose.yml up -d mosquitto
   ```

2. Start the router:
   ```bash
   python -m src.camel_router.cli --config examples/iot_routes.yaml
   ```

## Example Configuration

```yaml
routes:
  # Subscribe to sensor data
  - from:
      uri: "mqtt:sensors/+/temperature"
      parameters:
        brokerUrl: "tcp://localhost:1883"
    steps:
      - process:
          ref: "temperatureProcessor"
      - to: "log:iot"
      - choice:
          when:
            - simple: "${body} > 30"
              steps:
                - to: "mqtt:alerts/high_temperature"
```

## Testing the Example

1. The example includes simulated IoT devices that publish MQTT messages
2. The router processes these messages and can trigger alerts
3. Monitor the logs to see message flow:
   ```bash
   tail -f logs/router.log
   ```

## Security Considerations

- Always use TLS/SSL for production MQTT connections
- Implement proper authentication and authorization
- Consider using MQTT v5 features for better security

## Next Steps

- Add device provisioning flows
- Implement device shadowing
- Add support for IoT protocols like CoAP or LwM2M
