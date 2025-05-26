FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install grpcio-tools for protoc
RUN pip install --no-cache-dir grpcio-tools

# Copy protos and generate Python code
COPY protos/ /app/protos/
RUN python -m grpc_tools.protoc -I /app/protos \
    --python_out=/app --grpc_python_out=/app \
    /app/protos/example.proto

# Copy server and client code
COPY server.py .
COPY client.py .

# Copy the proto generated files (in case they're needed)
COPY protos/example_pb2.py .
COPY protos/example_pb2_grpc.py .

# Create a non-root user and switch to it
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose gRPC and metrics ports
EXPOSE 50051 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import grpc; channel = grpc.insecure_channel('localhost:50051'); \
    import example_pb2, example_pb2_grpc; \
    stub = example_pb2_grpc.GreeterStub(channel); \
    response = stub.SayHello(example_pb2.HelloRequest(name='healthcheck'), timeout=5); \
    print('Health check:', response.message)" || exit 1

# Start server
CMD ["python", "server.py"]
