#!/bin/bash

# Test gRPC service

echo "Testing gRPC service..."

# Check if grpcurl is installed
if ! command -v grpcurl &> /dev/null; then
    echo "grpcurl is not installed. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install grpcurl
    elif [[ -f /etc/debian_version ]]; then
        sudo apt-get update && sudo apt-get install -y grpcurl
    else
        echo "Please install grpcurl manually: https://github.com/fullstorydev/grpcurl"
        exit 1
    fi
fi

# Wait for the gRPC service to be ready
MAX_RETRIES=10
RETRY_COUNT=0
SLEEP_TIME=5

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if grpcurl -plaintext localhost:50051 list 2>/dev/null | grep -q "example.Greeter"; then
        echo "gRPC service is ready!"
        break
    else
        echo "Waiting for gRPC service to be ready... (Attempt $((RETRY_COUNT+1))/$MAX_RETRIES)"
        sleep $SLEEP_TIME
        RETRY_COUNT=$((RETRY_COUNT+1))
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "Timed out waiting for gRPC service to be ready"
    exit 1
fi

# Test unary RPC
echo -e "\nTesting unary RPC..."
grpcurl -plaintext -d '{"name": "Test User"}' localhost:50051 example.Greeter/SayHello

# Test server streaming
echo -e "\nTesting server streaming RPC..."
grpcurl -plaintext -d '{"count": 3, "prefix": "test"}' localhost:50051 example.Greeter/StreamData

# Test client streaming (using a simple Python script)
echo -e "\nTesting client streaming RPC..."
python3 -c "
import grpc
import example_pb2
import example_pb2_grpc

channel = grpc.insecure_channel('localhost:50051')
stub = example_pb2_grpc.GreeterStub(channel)

def generate_messages():
    for i in range(3):
        yield example_pb2.ClientMessage(
            client_id=f"client-{i}",
            message=f"Message {i+1}",
            sequence=i+1
        )

response = stub.ClientStream(generate_messages())
print(f'Server response: {response.response}')
print(f'Received sequence: {response.received_sequence}')
"

# Test bidirectional streaming
echo -e "\nTesting bidirectional streaming RPC..."
python3 -c "
import grpc
import example_pb2
import example_pb2_grpc

channel = grpc.insecure_channel('localhost:50051')
stub = example_pb2_grpc.GreeterStub(channel)

def generate_messages():
    for i in range(3):
        yield example_pb2.ClientMessage(
            client_id=f"client-{i}",
            message=f"Bidi {i+1}",
            sequence=i+1
        )

print('Sending messages and receiving responses:')
for response in stub.BidirectionalStream(generate_messages()):
    print(f'  - {response.response}')
"

# Test metrics endpoint
echo -e "\nTesting metrics endpoint..."
if command -v curl &> /dev/null; then
    curl -s http://localhost:8000/metrics | grep -E 'grpc_server_(requests_total|request_latency_seconds|active_requests)'
else
    echo "curl is not available. Please check http://localhost:8000/metrics manually."
fi

echo -e "\nAll tests completed!"
