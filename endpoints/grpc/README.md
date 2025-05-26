# gRPC Mock Service

A mock gRPC service for testing and development purposes. This service implements a simple gRPC API with various types of RPC methods.

## Features

- **Unary RPC**: Simple request/response pattern
- **Server Streaming RPC**: Server streams multiple responses
- **Client Streaming RPC**: Client streams multiple requests
- **Bidirectional Streaming RPC**: Both client and server stream messages
- **Prometheus Metrics**: Built-in metrics endpoint on port 8000
- **Health Check**: Simple health check endpoint

## Prerequisites

- Docker and Docker Compose (for containerized deployment)
- Python 3.7+ (for local development)
- gRPC tools (`pip install grpcio-tools`)

## Service Definition

The service is defined in `protos/example.proto` and includes the following methods:

```protobuf
service Greeter {
  // Simple RPC
  rpc SayHello (HelloRequest) returns (HelloReply) {}

  // Server streaming RPC
  rpc StreamData (DataRequest) returns (stream DataResponse) {}

  // Client streaming RPC
  rpc ClientStream (stream ClientMessage) returns (ServerResponse) {}

  // Bidirectional streaming RPC
  rpc BidirectionalStream (stream ClientMessage) returns (stream ServerResponse) {}
}
```

## Getting Started

### Building the Service

```bash
make build
```

### Running the Service

#### Using Docker (Recommended)

```bash
make docker-run
```

#### Running Locally

1. Install dependencies:

   ```bash
   pip install -r docker/requirements.txt
   ```

2. Generate gRPC code:

   ```bash
   make generate-protos
   ```

3. Run the server:
   ```bash
   make run-server
   ```

### Testing the Service

#### Using the Test Client

A Python test client is provided in `docker/client.py`:

```bash
# Run all tests
python docker/client.py

# Run specific test
python docker/client.py --test unary
python docker/client.py --test server_stream
python docker/client.py --test client_stream
python docker/client.py --test bidi
python docker/client.py --test health
```

#### Using Ansible

Run the Ansible test playbook:

```bash
make test
```

## API Documentation

### Unary RPC: SayHello

**Request**

```protobuf
message HelloRequest {
  string name = 1;
}
```

**Response**

```protobuf
message HelloReply {
  string message = 1;
  int32 status = 2;
}
```

### Server Streaming RPC: StreamData

**Request**

```protobuf
message DataRequest {
  int32 count = 1;
  string prefix = 2;
}
```

**Response** (stream)

```protobuf
message DataResponse {
  int32 id = 1;
  string value = 2;
  string timestamp = 3;
}
```

### Client Streaming RPC: ClientStream

**Request** (stream)

```protobuf
message ClientMessage {
  string client_id = 1;
  string message = 2;
  int32 sequence = 3;
}
```

**Response**

```protobuf
message ServerResponse {
  string server_id = 1;
  string response = 2;
  int32 received_sequence = 3;
  string timestamp = 4;
}
```

### Bidirectional Streaming RPC: BidirectionalStream

**Request** (stream)

```protobuf
message ClientMessage {
  string client_id = 1;
  string message = 2;
  int32 sequence = 3;
}
```

**Response** (stream)

```protobuf
message ServerResponse {
  string server_id = 1;
  string response = 2;
  int32 received_sequence = 3;
  string timestamp = 4;
}
```

## Monitoring

The service exposes Prometheus metrics on port 8000:

- `grpc_server_requests_total`: Total number of gRPC requests by method
- `grpc_server_request_latency_seconds`: Latency of gRPC requests by method
- `grpc_server_active_requests`: Number of active gRPC requests by method

## Development

### Generating gRPC Code

After modifying the `.proto` file, regenerate the gRPC code:

```bash
make generate-protos
```

### Running Tests

```bash
make test
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
