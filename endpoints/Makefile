.PHONY: help build test clean all test-grpc

# Default target
help:
	@echo "Available targets:"
	@echo "  build     - Build all endpoint containers"
	@echo "  up        - Start all endpoints"
	@echo "  down      - Stop all endpoints"
	@echo "  test      - Run all endpoint tests"
	@echo "  clean     - Clean up all endpoints"

# Build all endpoint containers
build:
	$(MAKE) -C rtsp build
	$(MAKE) -C http build
	$(MAKE) -C webrtc build
	$(MAKE) -C grpc build
	$(MAKE) -C mqtt build

# Start all endpoints
up:
	docker-compose -f docker-compose.yml up -d

# Stop all endpoints
down:
	docker-compose -f docker-compose.yml down

# Test all endpoints
test:
	ansible-playbook -i inventory.ini test.yml

# Test gRPC endpoint
test-grpc:
	$(MAKE) -C grpc test

# Clean up all endpoints
clean:
	$(MAKE) -C rtsp clean
	$(MAKE) -C http clean
	$(MAKE) -C webrtc clean
	$(MAKE) -C grpc clean
	$(MAKE) -C mqtt clean
	docker-compose -f docker-compose.yml down -v
