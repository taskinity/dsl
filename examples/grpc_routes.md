# gRPC Routes Example

This example demonstrates how to use Taskinity DSL with gRPC services. It includes both client and server examples for gRPC communication.

## Prerequisites

- Python 3.8 or higher
- gRPC tools (`pip install grpcio-tools`)
- Taskinity DSL installed
- Docker (for containerized services)

## Example Files

- `grpc_routes.yaml` - Main configuration file
- `docker-compose.yml` - Docker setup for gRPC services
- `proto/` - Protocol buffer definitions

## Running the Example

### Using Make (Recommended)

```bash
# Start the gRPC server and client
make run-example EXAMPLE=grpc

# View logs
make logs-example EXAMPLE=grpc

# Stop the example
make stop-example EXAMPLE=grpc
```

### Manual Execution

1. Start the gRPC server:

   ```bash
   python -m src.examples.grpc_server
   ```

2. In another terminal, start the router:
   ```bash
   python -m src.camel_router.cli --config examples/grpc_routes.yaml
   ```

## Example Configuration

```yaml
routes:
  - from:
      uri: "grpc://localhost:50051/example.Greeter"
      parameters:
        method: "SayHello"
        synchronous: true
    steps:
      - set-body:
          json: { "name": "Taskinity User" }
      - to: "log:info"
```

## Testing the Example

1. The example includes a simple gRPC service that echoes back messages
2. The router is configured to send requests to this service
3. Responses will be logged to the console

## Troubleshooting

- Ensure the gRPC server is running before starting the router
- Check port numbers match between client and server
- Verify protobuf definitions are compiled

## Next Steps

- Add more complex message transformations
- Implement error handling and retries
- Explore streaming gRPC endpoints
