# Taskinity DSL Examples

This directory contains example route configurations for the Taskinity DSL. Each example demonstrates different routing scenarios and features.

## Available Examples

1. [Simple Routes](simple_routes.md) - Basic routing examples
2. [gRPC Routes](grpc_routes.md) - gRPC service integration
3. [IoT Routes](iot_routes.md) - IoT device communication
4. [Camera Routes](camera_routes.md) - Video processing pipeline

## Running Examples

Each example can be started using the provided Makefile commands. Make sure you have the following installed:

- Python 3.8+
- Make
- Docker (for containerized examples)

### Basic Usage

```bash
# List all available examples
make list-examples

# Run a specific example
make run-example EXAMPLE=simple
```

## Development

To modify or create new examples, please follow the existing structure and update the documentation accordingly.
