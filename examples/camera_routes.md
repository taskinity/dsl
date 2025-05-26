# Camera Routes Example

This example demonstrates video processing pipelines using Taskinity DSL, including frame capture, object detection, and video streaming capabilities.

## Prerequisites

- Python 3.8 or higher
- OpenCV (`pip install opencv-python`)
- Taskinity DSL installed
- Docker (for containerized processing)
- Webcam or video file for input

## Example Files

- `camera_routes.yaml` - Main configuration file
- `docker-compose.yml` - Processing services
- `models/` - Pre-trained models
- `scripts/` - Processing scripts

## Running the Example

### Using Make (Recommended)

```bash
# Start the camera processing pipeline
make run-example EXAMPLE=camera

# View the processed video stream
make view-camera

# Stop the example
make stop-example EXAMPLE=camera
```

### Manual Execution

1. Start the processing services:

   ```bash
   docker-compose -f examples/docker-compose.yml up -d
   ```

2. Start the router:
   ```bash
   python -m src.camel_router.cli --config examples/camera_routes.yaml
   ```

## Example Configuration

```yaml
routes:
  # Capture frames from camera
  - from:
      uri: "direct:camera"
    steps:
      - process:
          ref: "frameCapture"
      - to: "direct:objectDetection"

  # Process frames with object detection
  - from:
      uri: "direct:objectDetection"
    steps:
      - process:
          ref: "objectDetector"
      - to: "direct:display"
```

## Testing the Example

1. The example will access your default camera (usually /dev/video0)
2. Processed frames will be displayed in a window
3. Detected objects will be highlighted with bounding boxes

## Performance Considerations

- Processing resolution impacts performance
- Consider frame skipping for better performance
- Use hardware acceleration when available (CUDA, OpenCL)

## Next Steps

- Add support for multiple cameras
- Implement motion detection
- Add video recording capabilities
- Integrate with cloud storage for processed videos
