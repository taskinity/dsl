# Mock Endpoints

This directory contains mock implementations of various protocol endpoints for testing the Taskinity DSL.

## Available Mock Services

1. **RTSP Server** - Mock RTSP video streaming server
2. **HTTP Server** - Mock HTTP/HTTPS REST API server
3. **WebRTC Server** - Mock WebRTC signaling server (TODO)
4. **gRPC Server** - Mock gRPC service with support for unary and streaming RPCs
5. **MQTT Broker** - Mock MQTT message broker (TODO)

## Quick Start

1. Build all services:

   ```bash
   make build
   ```

2. Start all services:

   ```bash
   make up
   ```

3. Run tests:

   ```bash
   make test
   ```

4. Stop all services:
   ```bash
   make down
   ```

## Service Details

### RTSP Server

- **Port**: 8554 (RTSP), 8888 (HTTP)
- **Test Stream**: `rtsp://localhost:8554/stream`
- **Build**: `make -C rtsp build`
- **Test**: `make -C rtsp test`

### HTTP Server

- **Port**: 8080
- **Base URL**: `http://localhost:8080`
- **Endpoints**:
  - `GET /` - Service status
  - `GET /api/data` - Sample data
  - `POST /api/echo` - Echo request data
  - `GET /api/status/{code}` - Return specified status code
- **Build**: `make -C http build`
- **Test**: `make -C http test`

### gRPC Server

- **Port**: 50051 (gRPC), 8000 (Prometheus metrics)
- **Service**: `example.Greeter`
- **Methods**:
  - `SayHello` - Simple unary RPC
  - `StreamData` - Server streaming RPC
  - `ClientStream` - Client streaming RPC
  - `BidirectionalStream` - Bidirectional streaming RPC
- **Build**: `make -C grpc build`
- **Test**: `make -C grpc test` or `make test-grpc`
- **Metrics**: `http://localhost:8000/metrics`
- **Test Client**: `python docker/client.py`

## Testing with Ansible

Run all tests:

```bash
ansible-playbook -i inventory.ini test.yml
```

Run specific service tests:

```bash
ansible-playbook -i inventory.ini test.yml --tags rtsp
ansible-playbook -i inventory.ini test.yml --tags http
```

## Development

To add a new mock service:

1. Create a new directory under `endpoints/`
2. Add `Makefile`, `docker/`, and `ansible/` subdirectories
3. Update the root `Makefile` and `test.yml` to include the new service
4. Add the service to `docker-compose.yml`

## Clean Up

To stop and remove all containers and images:

```bash
make clean
```
