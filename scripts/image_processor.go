package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"strconv"
	"time"
)

type InputData struct {
	Timestamp  string      `json:"timestamp"`
	Source     string      `json:"source"`
	Data       interface{} `json:"data"`
	Detections []Detection `json:"detections,omitempty"`
}

type Detection struct {
	ObjectType string    `json:"object_type"`
	Confidence float64   `json:"confidence"`
	BBox       []float64 `json:"bbox"`
	Position   string    `json:"position"`
}

type OutputData struct {
	Timestamp        string      `json:"timestamp"`
	Source           string      `json:"source"`
	ProcessedBy      string      `json:"processed_by"`
	EnhancedDetections []EnhancedDetection `json:"enhanced_detections"`
	ThreatLevel      string      `json:"threat_level"`
	ProcessingTime   float64     `json:"processing_time_ms"`
}

type EnhancedDetection struct {
	Detection
	RiskScore   float64 `json:"risk_score"`
	Zone        string  `json:"zone"`
	Action      string  `json:"recommended_action"`
}

func loadConfig() map[string]string {
	config := make(map[string]string)
	
	// Load configuration from environment variables set by Camel Router
	config["zone_mapping"] = getEnv("CONFIG_ZONE_MAPPING", "entrance:high,parking:medium,garden:low")
	config["threat_threshold"] = getEnv("CONFIG_THREAT_THRESHOLD", "0.7")
	config["processor_name"] = getEnv("CONFIG_PROCESSOR_NAME", "golang-image-processor")
	
	return config
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func calculateRiskScore(detection Detection, config map[string]string) float64 {
	baseRisk := detection.Confidence
	
	// Increase risk for certain object types
	switch detection.ObjectType {
	case "person":
		baseRisk *= 1.2
	case "car":
		baseRisk *= 0.8
	case "cat", "dog":
		baseRisk *= 0.3
	}
	
	// Increase risk for certain positions
	if detection.Position == "center-center" {
		baseRisk *= 1.1
	}
	
	return baseRisk
}

func determineZone(detection Detection) string {
	// Simple zone determination based on position
	// In real implementation, this would use actual coordinates
	switch detection.Position {
	case "center-center":
		return "entrance"
	case "bottom-left", "bottom-right":
		return "parking"
	default:
		return "perimeter"
	}
}

func recommendAction(riskScore float64, objectType string) string {
	if riskScore > 0.8 {
		if objectType == "person" {
			return "alert_security"
		}
		return "monitor_closely"
	} else if riskScore > 0.5 {
		return "log_event"
	}
	return "ignore"
}

func processDetections(input InputData, config map[string]string) OutputData {
	startTime := time.Now()
	
	var enhanced []EnhancedDetection
	maxRisk := 0.0
	
	for _, detection := range input.Detections {
		riskScore := calculateRiskScore(detection, config)
		zone := determineZone(detection)
		action := recommendAction(riskScore, detection.ObjectType)
		
		enhanced = append(enhanced, EnhancedDetection{
			Detection:   detection,
			RiskScore:   riskScore,
			Zone:        zone,
			Action:      action,
		})
		
		if riskScore > maxRisk {
			maxRisk = riskScore
		}
	}
	
	// Determine overall threat level
	threatLevel := "low"
	if maxRisk > 0.8 {
		threatLevel = "high"
	} else if maxRisk > 0.5 {
		threatLevel = "medium"
	}
	
	processingTime := float64(time.Since(startTime).Nanoseconds()) / 1e6 // Convert to milliseconds
	
	return OutputData{
		Timestamp:          time.Now().Format(time.RFC3339),
		Source:             input.Source,
		ProcessedBy:        config["processor_name"],
		EnhancedDetections: enhanced,
		ThreatLevel:        threatLevel,
		ProcessingTime:     processingTime,
	}
}

func main() {
	var inputFile = flag.String("input", "", "Input JSON file")
	var outputFile = flag.String("output", "", "Output JSON file (optional)")
	flag.Parse()
	
	if *inputFile == "" {
		log.Fatal("Input file is required")
	}
	
	// Load configuration
	config := loadConfig()
	
	// Read input file
	inputData, err := ioutil.ReadFile(*inputFile)
	if err != nil {
		log.Fatalf("Error reading input file: %v", err)
	}
	
	// Parse input JSON
	var input InputData
	if err := json.Unmarshal(inputData, &input); err != nil {
		log.Fatalf("Error parsing input JSON: %v", err)
	}
	
	// Process the data
	output := processDetections(input, config)
	
	// Convert output to JSON
	outputJSON, err := json.MarshalIndent(output, "", "  ")
	if err != nil {
		log.Fatalf("Error marshaling output: %v", err)
	}
	
	// Write output
	if *outputFile != "" {
		if err := ioutil.WriteFile(*outputFile, outputJSON, 0644); err != nil {
			log.Fatalf("Error writing output file: %v", err)
		}
	} else {
		fmt.Println(string(outputJSON))
	}
}