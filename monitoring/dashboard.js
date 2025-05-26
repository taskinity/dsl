/**
 * Camel Router Monitoring Dashboard
 * Real-time monitoring and metrics visualization
 */

class CamelRouterDashboard {
  constructor() {
    this.baseUrl = window.location.origin;
    this.wsUrl = `ws://${window.location.host}/ws`;
    this.refreshInterval = 5000; // 5 seconds
    this.websocket = null;
    this.charts = {};

    this.init();
  }

  async init() {
    this.setupEventListeners();
    this.connectWebSocket();
    this.startPeriodicRefresh();
    await this.loadInitialData();
  }

  setupEventListeners() {
    // Auto-refresh toggle
    const autoRefreshToggle = document.getElementById("auto-refresh");
    if (autoRefreshToggle) {
      autoRefreshToggle.addEventListener("change", (e) => {
        if (e.target.checked) {
          this.startPeriodicRefresh();
        } else {
          this.stopPeriodicRefresh();
        }
      });
    }

    // Refresh button
    const refreshButton = document.getElementById("refresh-btn");
    if (refreshButton) {
      refreshButton.addEventListener("click", () => this.refreshAll());
    }
  }

  connectWebSocket() {
    try {
      this.websocket = new WebSocket(this.wsUrl);

      this.websocket.onopen = () => {
        console.log("WebSocket connected");
        this.updateConnectionStatus("connected");
      };

      this.websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.handleRealtimeData(data);
      };

      this.websocket.onclose = () => {
        console.log("WebSocket disconnected");
        this.updateConnectionStatus("disconnected");
        // Attempt to reconnect after 5 seconds
        setTimeout(() => this.connectWebSocket(), 5000);
      };

      this.websocket.onerror = (error) => {
        console.error("WebSocket error:", error);
        this.updateConnectionStatus("error");
      };
    } catch (error) {
      console.log("WebSocket not available, using HTTP polling");
      this.updateConnectionStatus("polling");
    }
  }

  updateConnectionStatus(status) {
    const statusElement = document.getElementById("status");
    const statusDot = statusElement.querySelector(".status-dot");
    const statusText = statusElement.querySelector("span:last-child");

    statusDot.className = `status-dot ${status}`;

    switch (status) {
      case "connected":
        statusText.textContent = "Connected (WebSocket)";
        break;
      case "polling":
        statusText.textContent = "Connected (HTTP)";
        break;
      case "disconnected":
        statusText.textContent = "Disconnected";
        break;
      case "error":
        statusText.textContent = "Connection Error";
        break;
      default:
        statusText.textContent = "Connecting...";
    }
  }

  async loadInitialData() {
    try {
      await Promise.all([
        this.loadRoutesStatus(),
        this.loadMetrics(),
        this.loadRecentAlerts(),
        this.loadSystemHealth(),
      ]);
    } catch (error) {
      console.error("Error loading initial data:", error);
    }
  }

  async loadRoutesStatus() {
    try {
      const response = await fetch(`${this.baseUrl}/api/routes/status`);
      const data = await response.json();
      this.renderRoutesStatus(data);
    } catch (error) {
      console.error("Error loading routes status:", error);
      this.renderRoutesStatus(this.getMockRoutesData());
    }
  }

  async loadMetrics() {
    try {
      const response = await fetch(`${this.baseUrl}/api/metrics`);
      const data = await response.json();
      this.renderMetrics(data);
    } catch (error) {
      console.error("Error loading metrics:", error);
      this.renderMetrics(this.getMockMetricsData());
    }
  }

  async loadRecentAlerts() {
    try {
      const response = await fetch(`${this.baseUrl}/api/alerts/recent`);
      const data = await response.json();
      this.renderRecentAlerts(data);
    } catch (error) {
      console.error("Error loading recent alerts:", error);
      this.renderRecentAlerts(this.getMockAlertsData());
    }
  }

  async loadSystemHealth() {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      const data = await response.json();
      this.renderSystemHealth(data);
    } catch (error) {
      console.error("Error loading system health:", error);
      this.renderSystemHealth(this.getMockHealthData());
    }
  }

  renderRoutesStatus(data) {
    const container = document.getElementById("routes-status");

    const html = `
            <div class="routes-summary">
                <div class="metric">
                    <span class="metric-value">${data.total || 0}</span>
                    <span class="metric-label">Total Routes</span>
                </div>
                <div class="metric">
                    <span class="metric-value">${data.running || 0}</span>
                    <span class="metric-label">Running</span>
                </div>
                <div class="metric">
                    <span class="metric-value">${data.failed || 0}</span>
                    <span class="metric-label">Failed</span>
                </div>
            </div>
            <div class="routes-list">
                ${(data.routes || [])
                  .map(
                    (route) => `
                    <div class="route-item ${route.status}">
                        <div class="route-name">${route.name}</div>
                        <div class="route-status">${route.status}</div>
                        <div class="route-metrics">
                            <span>Messages: ${route.messages_processed || 0}</span>
                            <span>Uptime: ${this.formatDuration(route.uptime || 0)}</span>
                        </div>
                    </div>
                `,
                  )
                  .join("")}
            </div>
        `;

    container.innerHTML = html;
  }

  renderMetrics(data) {
    const container = document.getElementById("metrics");

    const html = `
            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>Messages Processed</h3>
                    <div class="metric-value">${data.messages_processed || 0}</div>
                    <div class="metric-change">+${data.messages_per_minute || 0}/min</div>
                </div>
                <div class="metric-card">
                    <h3>Processing Time</h3>
                    <div class="metric-value">${data.avg_processing_time || 0}ms</div>
                    <div class="metric-change">avg</div>
                </div>
                <div class="metric-card">
                    <h3>Error Rate</h3>
                    <div class="metric-value">${data.error_rate || 0}%</div>
                    <div class="metric-change ${data.error_rate > 5 ? "error" : "success"}">
                        ${data.error_rate > 5 ? "↑" : "↓"}
                    </div>
                </div>
                <div class="metric-card">
                    <h3>Memory Usage</h3>
                    <div class="metric-value">${data.memory_usage || 0}MB</div>
                    <div class="metric-change">${data.memory_percentage || 0}%</div>
                </div>
            </div>
        `;

    container.innerHTML = html;
  }

  renderRecentAlerts(data) {
    const container = document.getElementById("recent-alerts");

    if (!data.alerts || data.alerts.length === 0) {
      container.innerHTML = '<div class="no-data">No recent alerts</div>';
      return;
    }

    const html = `
            <div class="alerts-list">
                ${data.alerts
                  .map(
                    (alert) => `
                    <div class="alert-item ${alert.severity}">
                        <div class="alert-time">${this.formatTime(alert.timestamp)}</div>
                        <div class="alert-message">${alert.message}</div>
                        <div class="alert-source">${alert.source || "Unknown"}</div>
                    </div>
                `,
                  )
                  .join("")}
            </div>
        `;

    container.innerHTML = html;
  }

  renderSystemHealth(data) {
    const container = document.getElementById("system-health");

    const html = `
            <div class="health-overview">
                <div class="health-status ${data.status || "unknown"}">
                    <span class="health-indicator"></span>
                    <span class="health-label">${data.status || "Unknown"}</span>
                </div>
            </div>
            <div class="health-details">
                <div class="health-item">
                    <span class="health-metric">CPU Usage</span>
                    <span class="health-value">${data.cpu_usage || 0}%</span>
                </div>
                <div class="health-item">
                    <span class="health-metric">Memory Usage</span>
                    <span class="health-value">${data.memory_usage || 0}%</span>
                </div>
                <div class="health-item">
                    <span class="health-metric">Disk Usage</span>
                    <span class="health-value">${data.disk_usage || 0}%</span>
                </div>
                <div class="health-item">
                    <span class="health-metric">Active Connections</span>
                    <span class="health-value">${data.connections || 0}</span>
                </div>
            </div>
        `;

    container.innerHTML = html;
  }

  handleRealtimeData(data) {
    switch (data.type) {
      case "route_status":
        this.updateRouteStatus(data.payload);
        break;
      case "metrics":
        this.updateMetrics(data.payload);
        break;
      case "alert":
        this.addNewAlert(data.payload);
        break;
      case "health":
        this.updateSystemHealth(data.payload);
        break;
    }
  }

  updateRouteStatus(routeData) {
    // Update specific route in the UI
    const routeElement = document.querySelector(
      `[data-route="${routeData.name}"]`,
    );
    if (routeElement) {
      routeElement.className = `route-item ${routeData.status}`;
      routeElement.querySelector(".route-status").textContent =
        routeData.status;
    }
  }

  addNewAlert(alertData) {
    const alertsList = document.querySelector(".alerts-list");
    if (alertsList) {
      const alertHtml = `
                <div class="alert-item ${alertData.severity} new">
                    <div class="alert-time">${this.formatTime(alertData.timestamp)}</div>
                    <div class="alert-message">${alertData.message}</div>
                    <div class="alert-source">${alertData.source || "Unknown"}</div>
                </div>
            `;
      alertsList.insertAdjacentHTML("afterbegin", alertHtml);

      // Remove old alerts if too many
      const alerts = alertsList.querySelectorAll(".alert-item");
      if (alerts.length > 20) {
        alerts[alerts.length - 1].remove();
      }

      // Remove 'new' class after animation
      setTimeout(() => {
        const newAlert = alertsList.querySelector(".alert-item.new");
        if (newAlert) {
          newAlert.classList.remove("new");
        }
      }, 1000);
    }
  }

  startPeriodicRefresh() {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
    }

    this.refreshTimer = setInterval(() => {
      this.refreshAll();
    }, this.refreshInterval);
  }

  stopPeriodicRefresh() {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
      this.refreshTimer = null;
    }
  }

  async refreshAll() {
    await this.loadInitialData();
  }

  formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  }

  formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  }

  // Mock data for testing when backend is not available
  getMockRoutesData() {
    return {
      total: 4,
      running: 3,
      failed: 1,
      routes: [
        {
          name: "camera_detection",
          status: "running",
          messages_processed: 1234,
          uptime: 3600,
        },
        {
          name: "sensor_analytics",
          status: "running",
          messages_processed: 567,
          uptime: 2400,
        },
        {
          name: "alert_system",
          status: "failed",
          messages_processed: 89,
          uptime: 0,
        },
        {
          name: "health_monitor",
          status: "running",
          messages_processed: 45,
          uptime: 1800,
        },
      ],
    };
  }

  getMockMetricsData() {
    return {
      messages_processed: 15432,
      messages_per_minute: 45,
      avg_processing_time: 123,
      error_rate: 2.3,
      memory_usage: 512,
      memory_percentage: 25,
    };
  }

  getMockAlertsData() {
    return {
      alerts: [
        {
          timestamp: new Date().toISOString(),
          message: "Person detected in restricted area",
          severity: "high",
          source: "camera_detection",
        },
        {
          timestamp: new Date(Date.now() - 300000).toISOString(),
          message: "Sensor anomaly detected",
          severity: "medium",
          source: "sensor_analytics",
        },
        {
          timestamp: new Date(Date.now() - 600000).toISOString(),
          message: "System health check completed",
          severity: "low",
          source: "health_monitor",
        },
      ],
    };
  }

  getMockHealthData() {
    return {
      status: "healthy",
      cpu_usage: 45,
      memory_usage: 67,
      disk_usage: 23,
      connections: 12,
    };
  }
}

// Initialize dashboard when page loads
document.addEventListener("DOMContentLoaded", () => {
  new CamelRouterDashboard();
});
