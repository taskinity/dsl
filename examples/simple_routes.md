# Simple Routes Example

This example demonstrates basic routing with the Taskinity DSL. It shows how to create simple message routes between different endpoints.

## Prerequisites

- Python 3.8 or higher
- Taskinity DSL installed (`pip install -e .` from project root)

## Example Files

- `simple_routes.yaml` - Main configuration file
- `docker-compose.yml` - Optional Docker setup (if needed)

## Running the Example

### Using Make

```bash
# Start the simple routes example
make run-example EXAMPLE=simple

# View logs
make logs-example EXAMPLE=simple

# Stop the example
make stop-example EXAMPLE=simple
```

### Manual Execution

1. Start the router:
   ```bash
   python -m src.camel_router.cli --config examples/simple_routes.yaml
   ```

## Example Routes

```yaml
routes:
  - from:
      uri: "timer:tick"
      parameters:
        period: 1000
    steps:
      - set-body:
          constant: "Hello, World!"
      - to: "log:info"
```

## Expected Output

```
[INFO] Exchange[ExchangePattern: InOnly, BodyType: String, Body: Hello, World!]
```

## Next Steps

- Try modifying the route to send messages to different endpoints
- Add message transformation steps
- Explore other endpoint types in the documentation
