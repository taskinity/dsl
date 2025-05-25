# Taskinity DSL - Multi-Language ML/Media Processing Engine

🚀 **Apache Camel-style routing engine** for computer vision, machine learning, and multimedia processing pipelines that can delegate tasks to **multiple programming languages**.

## ✨ Features

- **📹 Real-time Video Processing**: RTSP cameras, streams, file inputs
- **🤖 Multi-Language Support**: Python, Go, Rust, C++, Node.js processors
- **🔗 Flexible Connectors**: Email, HTTP, gRPC, MQTT, file outputs  
- **🎯 ML-Ready**: Object detection, inference pipelines, TensorFlow integration
- **⚙️ Simple Configuration**: URL-style routing with .env support
- **🐳 Cloud Native**: Docker, Kubernetes, horizontal scaling
- **📊 Production Ready**: Monitoring, health checks, error handling

## 🏗️ Architecture

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────┐
│   Sources   │    │   Processors     │    │Destinations │
├─────────────┤    ├──────────────────┤    ├─────────────┤
│ RTSP Camera │───►│ Python: YOLO     │───►│ Email Alert │
│ Timer       │    │ Go: Risk Analysis│    │ HTTP Webhook│
│ MQTT Sensor │    │ Rust: Preprocessing│   │ MQTT Publish│
│ File Watch  │    │ C++: Optimization│    │ File Output │
│ gRPC Server │    │ Node.js: Rules   │    │ Log/Console │
└─────────────┘    └──────────────────┘    └─────────────┘
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/your-org/camel-router
cd camel-router

# Quick setup with Makefile
make quickstart
```

### 2. Configuration

Create your `.env` file:
```bash
# Copy template and edit
cp .env.example .env
```

Example `.env`:
```bash
CAMERA_USER=admin
CAMERA_PASS=your_password
CAMERA_IP=192.168.1.100
SMTP_USER=alerts@company.com
SMTP_PASS=app_password
SECURITY_EMAIL=security@company.com
```

### 3. Create Routes

Generate a configuration template:
```bash
camel-router init --template camera --output my_routes.yaml
```

Example route (simplified YAML):
```yaml
routes:
  - name: "smart_security_camera"
    from: "rtsp://{{CAMERA_USER}}:{{CAMERA_PASS}}@{{CAMERA_IP}}/stream1"
    
    processors:
      # Python: Object detection
      - type: "external"
        command: "python scripts/detect_objects.py"
        config:
          confidence_threshold: 0.6
          target_objects: ["person", "car"]
      
      # Go: Risk analysis  
      - type: "external"
        command: "go run scripts/image_processor.go"
        config:
          threat_threshold: 0.7
      
      # Filter high-risk only
      - type: "filter"
        condition: "{{threat_level}} == 'high'"
    
    to:
      - "email://{{SMTP_SERVER}}:{{SMTP_PORT}}?user={{SMTP_USER}}&password={{SMTP_PASS}}&to={{SECURITY_EMAIL}}"
      - "http://webhook.company.com/security-alert"
```

### 4. Run

```bash
# Run all routes
camel-router run -c my_routes.yaml

# Run specific route
camel-router run -c my_routes.yaml --route smart_security_camera

# Dry run to see what would execute
camel-router run -c my_routes.yaml --dry-run
```

## 📖 Detailed Usage

### Sources (Input)

| Source | Example URL | Description |
|--------|-------------|-------------|
| RTSP Camera | `rtsp://user:pass@ip/stream1` | Live video streams |
| Timer | `timer://5m` | Scheduled execution |
| File | `file:///path/to/watch` | File monitoring |
| gRPC | `grpc://localhost:50051/Service/Method` | gRPC endpoints |
| MQTT | `mqtt://broker:1883/topic` | MQTT messages |

### Processors (Transform)

#### External Processors
Delegate to any programming language:

```yaml
processors:
  # Python ML inference
  - type: "external"
    command: "python scripts/detect_objects.py"
    input_format: "json"
    output_format: "json"
    config:
      model: "yolov8n.pt"
      confidence_threshold: 0.6
  
  # Go image processing
  - type: "external"
    command: "go run scripts/image_processor.go"
    config:
      thread_count: 4
      optimization: "speed"
  
  # Rust performance-critical tasks
  - type: "external"
    command: "cargo run --bin data_processor"
    config:
      batch_size: 32
      simd_enabled: true
  
  # C++ optimized algorithms  
  - type: "external"
    command: "./bin/cpp_postprocessor"
    config:
      algorithm: "fast_nms"
      threshold: 0.85
  
  # Node.js business logic
  - type: "external"
    command: "node scripts/business_rules.js"
    config:
      rules_file: "security_rules.json"
```

#### Built-in Processors

```yaml
processors:
  # Filter messages
  - type: "filter"
    condition: "{{confidence}} > 0.7"
  
  # Transform output
  - type: "transform" 
    template: "Alert: {{object_type}} detected at {{position}}"
  
  # Aggregate over time
  - type: "aggregate"
    strategy: "collect"
    timeout: "5m"
    max_size: 100
```

### Destinations (Output)

| Destination | Example URL | Description |
|-------------|-------------|-------------|
| Email | `email://smtp.gmail.com:587?user={{USER}}&password={{PASS}}&to={{EMAILS}}` | SMTP alerts |
| HTTP | `http://api.company.com/webhook` | REST API calls |
| MQTT | `mqtt://broker:1883/alerts/camera` | MQTT publishing |
| File | `file:///logs/alerts.log` | File logging |
| gRPC | `grpc://service:50051/AlertService/Send` | gRPC calls |

## 🛠️ Development

### Project Structure

```
camel-router/
├── camel_router/           # Python package
│   ├── cli.py             # Command line interface
│   ├── engine.py          # Main routing engine
│   ├── processors.py      # Processing components
│   └── connectors.py      # Input/output connectors
├── scripts/               # External processors
│   ├── detect_objects.py  # Python: YOLO detection
│   ├── image_processor.go # Go: Risk analysis
│   ├── health_check.go    # Go: Health monitoring
│   └── business_rules.js  # Node.js: Business logic
├── examples/              # Configuration examples
│   └── simple_routes.yaml # Sample routes
├── k8s/                   # Kubernetes deployment
│   └── deployment.yaml    # K8s manifests
├── Dockerfile             # Container definition
├── Makefile              # Build automation
└── README.md             # This file
```

### Building External Processors

```bash
# Build all processors
make build-all

# Build specific language
make build-go
make build-rust
make build-cpp

# Install dependencies
make install-deps
```

### Development Workflow

```bash
# Development environment
make dev

# Run tests
make test

# Lint code
make lint

# Build distribution
make build
```

## 🐳 Docker Deployment

### Build and Run

```bash
# Build image
make docker

# Run with Docker
docker run -it --rm \
  -v $(PWD)/examples:/app/examples \
  -v $(PWD)/.env:/app/.env \
  camel-router:latest

# Or use Make
make docker-run
```

### Docker Compose (with dependencies)

```yaml
version: '3.8'
services:
  camel-router:
    build: .
    environment:
      - CAMERA_IP=192.168.1.100
      - MQTT_BROKER=mqtt
    volumes:
      - ./examples:/app/examples
      - ./logs:/app/logs
    depends_on:
      - mqtt
      - redis
  
  mqtt:
    image: eclipse-mosquitto:2
    ports:
      - "1883:1883"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

## ☸️ Kubernetes Deployment

```bash
# Deploy to Kubernetes
make deploy-k8s

# Or manually
kubectl apply -f k8s/

# Check status
kubectl get pods -n camel-router

# View logs
kubectl logs -f deployment/camel-router -n camel-router
```

Features in Kubernetes:
- **Horizontal Pod Autoscaling**: Auto-scale based on CPU/memory/custom metrics
- **Resource Management**: CPU/memory limits and requests
- **Health Checks**: Liveness and readiness probes
- **Persistent Storage**: Shared volumes for model files and logs
- **Service Discovery**: Internal service communication
- **Monitoring**: Prometheus metrics integration

## 📊 Monitoring and Observability

### Built-in Metrics

```bash
# Health check endpoint
curl http://localhost:8080/health

# Metrics endpoint (Prometheus format)
curl http://localhost:8080/metrics

# Runtime statistics
curl http://localhost:8080/stats
```

### Logging

```bash
# View real-time logs
make logs

# Start monitoring dashboard  
make monitor
```

### Performance Benchmarking

```bash
# Run benchmarks
make benchmark
```

## 🔧 Configuration Reference

### Environment Variables

```bash
# Camera settings
CAMERA_USER=admin
CAMERA_PASS=password  
CAMERA_IP=192.168.1.100
CAMERA_NAME=front_door

# Email settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@company.com
SMTP_PASS=app_password
SECURITY_EMAIL=security@company.com

# Service URLs
WEBHOOK_URL=https://hooks.company.com
ML_GRPC_SERVER=localhost:50051
DASHBOARD_URL=https://dashboard.company.com

# MQTT settings
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_USER=camel_router
MQTT_PASS=secret

# Advanced settings
MAX_CONCURRENT_ROUTES=10
DEFAULT_TIMEOUT=30
LOG_LEVEL=info
METRICS_ENABLED=true
```

### Route Configuration Schema

```yaml
routes:
  - name: "route_name"                    # Required: Route identifier
    from: "source_uri"                    # Required: Input source  
    processors:                           # Optional: Processing pipeline
      - type: "processor_type"
        config: {}
    to: ["destination_uri"]               # Required: Output destinations

# Global settings
settings:
  max_concurrent_routes: 10
  default_timeout: 30
  log_level: "info"
  metrics_enabled: true
  health_check_port: 8080

# Required environment variables
env_vars:
  - CAMERA_USER
  - SMTP_PASS
```

## 🎯 Use Cases

### 1. Smart Security System
- **Input**: RTSP cameras, motion sensors
- **Processing**: Python (YOLO), Go (risk analysis), Node.js (rules)
- **Output**: Email alerts, mobile push, dashboard

### 2. Industrial Quality Control
- **Input**: Factory cameras, sensor data
- **Processing**: Python (defect detection), C++ (performance), Rust (safety)
- **Output**: MQTT control, database, operator alerts

### 3. IoT Data Pipeline  
- **Input**: MQTT sensors, HTTP APIs
- **Processing**: Go (aggregation), Python (analytics), Node.js (business logic)
- **Output**: Time-series DB, real-time dashboard, alerts

### 4. Media Processing Pipeline
- **Input**: File uploads, streaming video
- **Processing**: Python (ML inference), C++ (codec), Rust (optimization)
- **Output**: CDN upload, metadata database, webhooks

## 🔍 Troubleshooting

### Common Issues

#### Camera Connection Failed
```bash
# Test RTSP connection
ffmpeg -i rtsp://user:pass@ip/stream1 -frames:v 1 test.jpg

# Check network connectivity
ping camera_ip
telnet camera_ip 554
```

#### External Processor Errors
```bash
# Test processor manually
echo '{"test": "data"}' | python scripts/detect_objects.py --input /dev/stdin

# Check dependencies
which go python node cargo

# View processor logs
camel-router run -c config.yaml --verbose
```

#### Performance Issues
```bash
# Monitor resource usage
htop

# Check route performance
make benchmark

# Optimize configuration
# - Reduce frame processing rate
# - Increase batch sizes
# - Use async processors
```

### Debug Mode

```bash
# Enable verbose logging
camel-router run -c config.yaml --verbose

# Dry run to test configuration
camel-router run -c config.yaml --dry-run

# Validate configuration
camel-router validate -c config.yaml
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Run checks: `make dev-workflow`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open Pull Request

### Development Setup

```bash
# Clone and setup
git clone https://github.com/your-org/camel-router
cd camel-router
make dev

# Run tests
make test

# Check code quality
make lint
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- **[Apache Camel](https://camel.apache.org/)**: Original enterprise integration framework
- **[GStreamer](https://gstreamer.freedesktop.org/)**: Multimedia framework
- **[Apache NiFi](https://nifi.apache.org/)**: Data flow automation
- **[Kubeflow](https://kubeflow.org/)**: ML workflows on Kubernetes
- **[TensorFlow Serving](https://tensorflow.org/tfx/serving)**: ML model serving

## 💡 Roadmap

- [ ] **Web UI**: Visual route designer and monitoring dashboard
- [ ] **More Connectors**: Database, cloud storage, message queues
- [ ] **Model Registry**: Integration with MLflow, DVC
- [ ] **Stream Processing**: Apache Kafka, Apache Pulsar support
- [ ] **Auto-scaling**: Dynamic processor scaling based on load
- [ ] **Security**: End-to-end encryption, authentication, authorization
- [ ] **Templates**: Pre-built templates for common use cases

---

**Built with ❤️ for the ML and multimedia processing community**

[⭐ Star us on GitHub](https://github.com/your-org/camel-router) | [📖 Documentation](https://docs.camel-router.org) | [💬 Community](https://discord.gg/camel-router)