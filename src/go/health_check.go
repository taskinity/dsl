package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"
	"time"
)

type HealthInput struct {
	Timestamp string `json:"timestamp"`
	Trigger   string `json:"trigger"`
}

type ServiceHealth struct {
	Service    string  `json:"service"`
	URL        string  `json:"url"`
	Status     string  `json:"status"`
	ResponseTime float64 `json:"response_time_ms"`
	Error      string  `json:"error,omitempty"`
}

type HealthOutput struct {
	Timestamp    string          `json:"timestamp"`
	OverallStatus string         `json:"status"`
	Services     []ServiceHealth `json:"services"`
	HealthyCount int            `json:"healthy_count"`
	TotalCount   int            `json:"total_count"`
}

func checkService(url string, timeout time.Duration) ServiceHealth {
	start := time.Now()
	
	client := &http.Client{Timeout: timeout}
	resp, err := client.Get(url)
	
	responseTime := float64(time.Since(start).Nanoseconds()) / 1e6
	
	service := ServiceHealth{
		Service:      extractServiceName(url),
		URL:          url,
		ResponseTime: responseTime,
	}
	
	if err != nil {
		service.Status = "unhealthy"
		service.Error = err.Error()
		return service
	}
	defer resp.Body.Close()
	
	if resp.StatusCode >= 200 && resp.StatusCode < 300 {
		service.Status = "healthy"
	} else {
		service.Status = "unhealthy"
		service.Error = fmt.Sprintf("HTTP %d", resp.StatusCode)
	}
	
	return service
}

func extractServiceName(url string) string {
	parts := strings.Split(url, "/")
	if len(parts) >= 3 {
		return parts[2] // hostname:port
	}
	return url
}

func main() {
	var inputFile = flag.String("input", "", "Input JSON file")
	var outputFile = flag.String("output", "", "Output JSON file (optional)")
	flag.Parse()
	
	if *inputFile == "" {
		log.Fatal("Input file is required")
	}
	
	// Load configuration from environment
	endpoints := os.Getenv("CONFIG_CHECK_ENDPOINTS")
	if endpoints == "" {
		endpoints = "http://localhost:8080/health"
	}
	
	timeoutStr := os.Getenv("CONFIG_TIMEOUT")
	timeout, err := time.ParseDuration(timeoutStr + "s")
	if err != nil {
		timeout = 10 * time.Second
	}
	
	// Parse endpoints
	urls := strings.Split(endpoints, ",")
	
	// Check all services
	var services []ServiceHealth
	healthyCount := 0
	
	for _, url := range urls {
		url = strings.TrimSpace(url)
		if url == "" {
			continue
		}
		
		health := checkService(url, timeout)
		services = append(services, health)
		
		if health.Status == "healthy" {
			healthyCount++
		}
	}
	
	// Determine overall status
	overallStatus := "healthy"
	if healthyCount == 0 {
		overallStatus = "critical"
	} else if healthyCount < len(services) {
		overallStatus = "degraded"
	}
	
	// Create output
	output := HealthOutput{
		Timestamp:     time.Now().Format(time.RFC3339),
		OverallStatus: overallStatus,
		Services:      services,
		HealthyCount:  healthyCount,
		TotalCount:    len(services),
	}
	
	// Convert to JSON
	outputJSON, err := json.MarshalIndent(output, "", "  ")
	if err != nil {
		log.Fatalf("Error marshaling output: %v", err)
	}
	
	// Write output
	if *outputFile != "" {
		if err := os.WriteFile(*outputFile, outputJSON, 0644); err != nil {
			log.Fatalf("Error writing output file: %v", err)
		}
	} else {
		fmt.Println(string(outputJSON))
	}
}