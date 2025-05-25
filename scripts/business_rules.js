#!/usr/bin/env node
/**
 * Node.js Business Rules Processor
 * Handles complex business logic and decision making
 */

const fs = require('fs');
const path = require('path');

// Configuration from environment variables
const config = {
    rulesFile: process.env.CONFIG_RULES_FILE || 'security_rules.json',
    alertThreshold: parseFloat(process.env.CONFIG_ALERT_THRESHOLD || '0.7'),
    businessHours: process.env.CONFIG_BUSINESS_HOURS || '09:00-17:00',
    escalationTime: parseInt(process.env.CONFIG_ESCALATION_TIME || '300') // seconds
};

class BusinessRulesEngine {
    constructor() {
        this.rules = this.loadRules();
    }

    loadRules() {
        try {
            if (fs.existsSync(config.rulesFile)) {
                return JSON.parse(fs.readFileSync(config.rulesFile, 'utf8'));
            }
        } catch (error) {
            console.error(`Error loading rules: ${error.message}`);
        }
        
        // Default rules
        return {
            person_detection: {
                business_hours: { priority: 'medium', action: 'log' },
                after_hours: { priority: 'high', action: 'alert' },
                restricted_zones: { priority: 'critical', action: 'immediate_alert' }
            },
            vehicle_detection: {
                parking_area: { priority: 'low', action: 'log' },
                restricted_area: { priority: 'high', action: 'alert' }
            },
            threat_assessment: {
                high_confidence: { threshold: 0.8, action: 'escalate' },
                medium_confidence: { threshold: 0.6, action: 'monitor' },
                low_confidence: { threshold: 0.3, action: 'log' }
            }
        };
    }

    isBusinessHours() {
        const now = new Date();
        const currentTime = now.getHours() * 100 + now.getMinutes();
        const [start, end] = config.businessHours.split('-').map(time => {
            const [hours, minutes] = time.split(':').map(Number);
            return hours * 100 + minutes;
        });
        return currentTime >= start && currentTime <= end;
    }

    processDetection(detection) {
        const { object_type, confidence, zone, position } = detection;
        const isAfterHours = !this.isBusinessHours();
        
        let decision = {
            original_detection: detection,
            business_priority: 'low',
            recommended_action: 'log',
            escalation_required: false,
            business_context: {},
            timestamp: new Date().toISOString()
        };

        // Apply object-specific rules
        if (object_type === 'person') {
            if (zone === 'restricted' || zone === 'entrance') {
                decision.business_priority = 'critical';
                decision.recommended_action = 'immediate_alert';
                decision.escalation_required = true;
            } else if (isAfterHours) {
                decision.business_priority = 'high';
                decision.recommended_action = 'alert';
            } else {
                decision.business_priority = 'medium';
                decision.recommended_action = 'monitor';
            }
        }

        if (object_type === 'car') {
            if (zone === 'parking') {
                decision.business_priority = 'low';
                decision.recommended_action = 'log';
            } else {
                decision.business_priority = 'medium';
                decision.recommended_action = 'monitor';
            }
        }

        // Apply confidence-based rules
        if (confidence > 0.8) {
            decision.business_priority = this.raisePriority(decision.business_priority);
        }

        // Add business context
        decision.business_context = {
            is_business_hours: !isAfterHours,
            zone_risk_level: this.getZoneRiskLevel(zone),
            time_based_modifier: isAfterHours ? 1.5 : 1.0,
            requires_immediate_response: decision.business_priority === 'critical'
        };

        return decision;
    }

    raisePriority(currentPriority) {
        const priorities = ['low', 'medium', 'high', 'critical'];
        const currentIndex = priorities.indexOf(currentPriority);
        return priorities[Math.min(currentIndex + 1, priorities.length - 1)];
    }

    getZoneRiskLevel(zone) {
        const riskLevels = {
            'entrance': 'high',
            'restricted': 'critical',
            'parking': 'low',
            'perimeter': 'medium',
            'garden': 'low'
        };
        return riskLevels[zone] || 'medium';
    }

    processAggregatedEvents(events) {
        const decisions = events.map(event => this.processDetection(event));
        
        // Analyze patterns
        const patterns = this.analyzePatterns(decisions);
        
        return {
            individual_decisions: decisions,
            pattern_analysis: patterns,
            overall_threat_level: this.calculateOverallThreat(decisions),
            recommended_actions: this.recommendActions(decisions, patterns)
        };
    }

    analyzePatterns(decisions) {
        const patterns = {
            repeated_detections: {},
            zone_clustering: {},
            time_clustering: {},
            escalation_pattern: false
        };

        // Count detections by type and zone
        decisions.forEach(decision => {
            const key = `${decision.original_detection.object_type}_${decision.original_detection.zone}`;
            patterns.repeated_detections[key] = (patterns.repeated_detections[key] || 0) + 1;
        });

        // Check for escalation pattern
        const criticalCount = decisions.filter(d => d.business_priority === 'critical').length;
        patterns.escalation_pattern = criticalCount > 1;

        return patterns;
    }

    calculateOverallThreat(decisions) {
        const priorityWeights = { low: 1, medium: 2, high: 3, critical: 4 };
        const totalWeight = decisions.reduce((sum, decision) => {
            return sum + priorityWeights[decision.business_priority];
        }, 0);
        
        const avgWeight = totalWeight / decisions.length;
        
        if (avgWeight >= 3.5) return 'critical';
        if (avgWeight >= 2.5) return 'high';
        if (avgWeight >= 1.5) return 'medium';
        return 'low';
    }

    recommendActions(decisions, patterns) {
        const actions = [];
        
        if (patterns.escalation_pattern) {
            actions.push({
                type: 'escalate_to_security',
                priority: 'immediate',
                reason: 'Multiple critical events detected'
            });
        }

        const highPriorityCount = decisions.filter(d => 
            ['high', 'critical'].includes(d.business_priority)
        ).length;

        if (highPriorityCount > 2) {
            actions.push({
                type: 'notify_management',
                priority: 'urgent',
                reason: 'Multiple high-priority security events'
            });
        }

        return actions;
    }
}

// Main execution
async function main() {
    const inputFile = process.argv.find(arg => arg.startsWith('--input'))?.split('=')[1];
    const outputFile = process.argv.find(arg => arg.startsWith('--output'))?.split('=')[1];

    if (!inputFile) {
        console.error('Input file required: --input=file.json');
        process.exit(1);
    }

    try {
        const inputData = JSON.parse(fs.readFileSync(inputFile, 'utf8'));
        const engine = new BusinessRulesEngine();

        let result;
        if (Array.isArray(inputData.detections)) {
            result = engine.processAggregatedEvents(inputData.detections);
        } else if (inputData.enhanced_detections) {
            result = engine.processAggregatedEvents(inputData.enhanced_detections);
        } else {
            result = engine.processDetection(inputData);
        }

        const output = {
            timestamp: new Date().toISOString(),
            processor: 'business_rules_engine',
            input_source: inputData.source || 'unknown',
            business_analysis: result
        };

        if (outputFile) {
            fs.writeFileSync(outputFile, JSON.stringify(output, null, 2));
        } else {
            console.log(JSON.stringify(output, null, 2));
        }

    } catch (error) {
        const errorOutput = {
            error: error.message,
            processor: 'business_rules_engine',
            success: false
        };
        console.error(JSON.stringify(errorOutput, null, 2));
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = { BusinessRulesEngine };