# Monitoring Dashboard

The Taskinity DSL includes a built-in monitoring dashboard to help you track and visualize the performance of your dialog processing pipelines.

## Features

- Real-time metrics visualization
- System resource monitoring
- Message processing statistics
- Error tracking and alerts

## Prerequisites

- Python 3.6 or higher
- Web browser

## Starting the Monitoring Dashboard

1. Navigate to your project root directory
2. Run the following command:
   ```bash
   make monitoring
   ```
3. Open your web browser and go to: http://localhost:8000

## Stopping the Monitoring Dashboard

To stop the monitoring dashboard, run:

```bash
make monitoring-stop
```

## Dashboard Components

### 1. System Metrics
- CPU usage
- Memory usage
- Network I/O
- Disk I/O

### 2. Message Processing
- Messages processed per second
- Average processing time
- Error rate
- Queue sizes

### 3. Alerts
- Critical errors
- Warning messages
- Performance degradation

## Configuration

You can configure the monitoring dashboard by creating a `monitoring/config.json` file with the following options:

```json
{
  "port": 8000,
  "refresh_interval": 5000,
  "metrics_endpoint": "/api/metrics",
  "retention_period": "24h"
}
```

## Troubleshooting

### Dashboard not loading
- Ensure no other service is using port 8000
- Check that all required files are present in the `monitoring` directory
- Verify that Python can access the required modules

### No data showing
- Confirm that your application is sending metrics to the dashboard
- Check the browser's developer console for errors
- Verify network connectivity between your application and the dashboard

## Security Considerations

- The monitoring dashboard should not be exposed to the public internet
- Use authentication if exposing the dashboard over a network
- Regularly update the dashboard components to the latest versions

## Advanced Usage

### Custom Metrics
You can add custom metrics by extending the dashboard's JavaScript code in `monitoring/dashboard.js`.

### Persistent Storage
For production use, consider integrating with a time-series database like InfluxDB or Prometheus for long-term metric storage.

### Alerting
Set up alerts by configuring the `alerts` section in the configuration file to notify you of critical conditions.
