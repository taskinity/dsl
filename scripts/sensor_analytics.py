#!/usr/bin/env python3
"""
Python Sensor Analytics Processor
Performs anomaly detection and statistical analysis on sensor data
"""

import sys
import json
import argparse
import os
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import deque
import statistics

class SensorAnalytics:
    def __init__(self):
        self.anomaly_threshold = float(os.getenv('CONFIG_ANOMALY_THRESHOLD', '2.5'))
        self.window_size = int(os.getenv('CONFIG_WINDOW_SIZE', '100'))
        self.min_samples = int(os.getenv('CONFIG_MIN_SAMPLES', '10'))
        
        # In-memory storage for this session
        self.sensor_history = {}
        
    def detect_anomalies(self, sensor_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect anomalies in sensor data using statistical methods"""
        anomalies = []
        processed_sensors = {}
        
        for reading in sensor_data:
            sensor_id = reading.get('sensor_id', 'unknown')
            value = reading.get('value', 0)
            timestamp = reading.get('timestamp', datetime.now().isoformat())
            
            if sensor_id not in self.sensor_history:
                self.sensor_history[sensor_id] = deque(maxlen=self.window_size)
            
            history = self.sensor_history[sensor_id]
            history.append(value)
            
            if len(history) >= self.min_samples:
                # Calculate z-score for anomaly detection
                mean_val = statistics.mean(history)
                std_val = statistics.stdev(history) if len(history) > 1 else 0
                
                if std_val > 0:
                    z_score = abs(value - mean_val) / std_val
                    is_anomaly = z_score > self.anomaly_threshold
                else:
                    is_anomaly = False
                    z_score = 0
                
                sensor_stats = {
                    'sensor_id': sensor_id,
                    'current_value': value,
                    'mean': mean_val,
                    'std': std_val,
                    'z_score': z_score,
                    'is_anomaly': is_anomaly,
                    'timestamp': timestamp,
                    'sample_count': len(history)
                }
                
                processed_sensors[sensor_id] = sensor_stats
                
                if is_anomaly:
                    anomalies.append({
                        'sensor_id': sensor_id,
                        'value': value,
                        'expected_range': [mean_val - 2*std_val, mean_val + 2*std_val],
                        'z_score': z_score,
                        'severity': self.classify_severity(z_score),
                        'timestamp': timestamp
                    })
        
        return {
            'anomalies': anomalies,
            'sensor_statistics': processed_sensors,
            'total_sensors': len(processed_sensors),
            'anomaly_count': len(anomalies)
        }
    
    def classify_severity(self, z_score: float) -> str:
        """Classify anomaly severity based on z-score"""
        if z_score > 4:
            return 'critical'
        elif z_score > 3:
            return 'high'
        elif z_score > 2.5:
            return 'medium'
        else:
            return 'low'
    
    def analyze_trends(self, sensor_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends in sensor data"""
        trends = {}
        
        # Group by sensor
        sensors = {}
        for reading in sensor_data:
            sensor_id = reading.get('sensor_id', 'unknown')
            if sensor_id not in sensors:
                sensors[sensor_id] = []
            sensors[sensor_id].append(reading)
        
        for sensor_id, readings in sensors.items():
            if len(readings) < 3:
                continue
                
            values = [r.get('value', 0) for r in readings]
            timestamps = [r.get('timestamp') for r in readings]
            
            # Simple trend analysis
            if len(values) >= 2:
                trend_direction = 'stable'
                if values[-1] > values[0]:
                    trend_direction = 'increasing'
                elif values[-1] < values[0]:
                    trend_direction = 'decreasing'
                
                rate_of_change = (values[-1] - values[0]) / len(values)
                
                trends[sensor_id] = {
                    'direction': trend_direction,
                    'rate_of_change': rate_of_change,
                    'min_value': min(values),
                    'max_value': max(values),
                    'avg_value': statistics.mean(values),
                    'value_range': max(values) - min(values),
                    'sample_count': len(values)
                }
        
        return trends
    
    def generate_alerts(self, anomalies: List[Dict[str, Any]], trends: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate alerts based on anomalies and trends"""
        alerts = []
        
        # Anomaly-based alerts
        for anomaly in anomalies:
            if anomaly['severity'] in ['critical', 'high']:
                alerts.append({
                    'type': 'anomaly_alert',
                    'sensor_id': anomaly['sensor_id'],
                    'message': f"Anomaly detected: {anomaly['sensor_id']} value {anomaly['value']} (z-score: {anomaly['z_score']:.2f})",
                    'severity': anomaly['severity'],
                    'timestamp': anomaly['timestamp'],
                    'recommended_action': 'investigate_sensor' if anomaly['severity'] == 'critical' else 'monitor_closely'
                })
        
        # Trend-based alerts
        for sensor_id, trend in trends.items():
            if abs(trend['rate_of_change']) > 10:  # Configurable threshold
                alerts.append({
                    'type': 'trend_alert',
                    'sensor_id': sensor_id,
                    'message': f"Rapid change detected: {sensor_id} changing at rate {trend['rate_of_change']:.2f}",
                    'severity': 'medium',
                    'timestamp': datetime.now().isoformat(),
                    'trend_direction': trend['direction'],
                    'recommended_action': 'check_sensor_calibration'
                })
        
        return alerts

def main():
    parser = argparse.ArgumentParser(description='Sensor Analytics Processor')
    parser.add_argument('--input', required=True, help='Input JSON file')
    parser.add_argument('--output', help='Output JSON file (optional)')
    
    args = parser.parse_args()
    
    try:
        with open(args.input, 'r') as f:
            input_data = json.load(f)
        
        analytics = SensorAnalytics()
        
        # Extract sensor data from input
        if 'events' in input_data:
            sensor_data = input_data['events']
        elif isinstance(input_data, list):
            sensor_data = input_data
        else:
            sensor_data = [input_data]
        
        # Perform analysis
        anomaly_results = analytics.detect_anomalies(sensor_data)
        trend_results = analytics.analyze_trends(sensor_data)
        alerts = analytics.generate_alerts(anomaly_results['anomalies'], trend_results)
        
        output = {
            'timestamp': datetime.now().isoformat(),
            'processor': 'sensor_analytics',
            'input_count': len(sensor_data),
            'anomaly_analysis': anomaly_results,
            'trend_analysis': trend_results,
            'alerts': alerts,
            'summary': {
                'total_anomalies': len(anomaly_results['anomalies']),
                'critical_anomalies': len([a for a in anomaly_results['anomalies'] if a['severity'] == 'critical']),
                'total_alerts': len(alerts),
                'sensors_analyzed': len(trend_results)
            }
        }
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(output, f, indent=2)
        else:
            print(json.dumps(output, indent=2))
    
    except Exception as e:
        error_output = {
            'error': str(e),
            'processor': 'sensor_analytics',
            'success': False
        }
        print(json.dumps(error_output, indent=2), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()