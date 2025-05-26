#!/usr/bin/env node
/**
 * Node.js Alerting Engine
 * Handles multi-channel notifications and escalation
 */

const fs = require('fs');
const https = require('https');
const http = require('http');

const config = {
    alertChannels: (process.env.CONFIG_ALERT_CHANNELS || 'email,webhook').split(','),
    escalationRules: process.env.CONFIG_ESCALATION_RULES || 'immediate:critical,5min:high,1h:medium',
    webhookUrl: process.env.CONFIG_WEBHOOK_URL || 'http://localhost:8080/webhook',
    slackWebhook: process.env.CONFIG_SLACK_WEBHOOK || '',
    maxRetries: parseInt(process.env.CONFIG_MAX_RETRIES || '3')
};

class AlertingEngine {
    constructor() {
        this.escalationRules = this.parseEscalationRules();
        this.alertHistory = new Map();
    }

    parseEscalationRules() {
        const rules = {};
        config.escalationRules.split(',').forEach(rule => {
            const [time, severity] = rule.split(':');
            rules[severity] = this.parseTimeToSeconds(time);
        });
        return rules;
    }

    parseTimeToSeconds(timeStr) {
        if (timeStr === 'immediate') return 0;
        
        const value = parseInt(timeStr);
        if (timeStr.endsWith('min')) return value * 60;
        if (timeStr.endsWith('h')) return value * 3600;
        if (timeStr.endsWith('s')) return value;
        return value; // assume seconds
    }

    async processAlerts(alertData) {
        const alerts = Array.isArray(alertData.alerts) ? alertData.alerts : [alertData];
        const results = [];

        for (const alert of alerts) {
            const result = await this.processAlert(alert);
            results.push(result);
        }

        return {
            processed_alerts: results,
            total_alerts: alerts.length,
            successful_deliveries: results.filter(r => r.success).length,
            failed_deliveries: results.filter(r => !r.success).length
        };
    }

    async processAlert(alert) {
        const alertId = this.generateAlertId(alert);
        const severity = alert.severity || 'medium';
        const escalationDelay = this.escalationRules[severity] || 300;

        const alertResult = {
            alert_id: alertId,
            severity: severity,
            escalation_delay: escalationDelay,
            channels_used: [],
            success: false,
            delivery_results: []
        };

        // Immediate processing for critical alerts
        if (severity === 'critical' || escalationDelay === 0) {
            return await this.deliverAlert(alert, alertResult);
        }

        // Schedule escalation for non-critical alerts
        this.scheduleEscalation(alert, alertResult, escalationDelay);
        
        return alertResult;
    }

    async deliverAlert(alert, alertResult) {
        const deliveryPromises = [];

        for (const channel of config.alertChannels) {
            switch (channel.trim()) {
                case 'webhook':
                    deliveryPromises.push(this.sendWebhook(alert));
                    break;
                case 'slack':
                    if (config.slackWebhook) {
                        deliveryPromises.push(this.sendSlack(alert));
                    }
                    break;
                case 'email':
                    deliveryPromises.push(this.sendEmail(alert));
                    break;
                default:
                    console.warn(`Unknown alert channel: ${channel}`);
            }
        }

        try {
            const results = await Promise.allSettled(deliveryPromises);
            
            results.forEach((result, index) => {
                const channel = config.alertChannels[index];
                alertResult.delivery_results.push({
                    channel: channel,
                    success: result.status === 'fulfilled',
                    error: result.status === 'rejected' ? result.reason : null
                });
                
                if (result.status === 'fulfilled') {
                    alertResult.channels_used.push(channel);
                }
            });

            alertResult.success = alertResult.channels_used.length > 0;
            
        } catch (error) {
            alertResult.error = error.message;
        }

        return alertResult;
    }

    async sendWebhook(alert) {
        return new Promise((resolve, reject) => {
            const payload = JSON.stringify({
                alert_type: 'camel_router_alert',
                timestamp: new Date().toISOString(),
                severity: alert.severity,
                message: alert.message || 'Alert triggered',
                source: alert.source || 'camel_router',
                details: alert
            });

            const url = new URL(config.webhookUrl);
            const options = {
                hostname: url.hostname,
                port: url.port || (url.protocol === 'https:' ? 443 : 80),
                path: url.pathname + url.search,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Content-Length': Buffer.byteLength(payload)
                }
            };

            const client = url.protocol === 'https:' ? https : http;
            const req = client.request(options, (res) => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    resolve({ channel: 'webhook', status: 'success' });
                } else {
                    reject(new Error(`Webhook failed with status ${res.statusCode}`));
                }
            });

            req.on('error', (error) => {
                reject(new Error(`Webhook request failed: ${error.message}`));
            });

            req.write(payload);
            req.end();
        });
    }

    async sendSlack(alert) {
        if (!config.slackWebhook) {
            throw new Error('Slack webhook URL not configured');
        }

        const payload = JSON.stringify({
            text: `🚨 Alert: ${alert.message || 'Camel Router Alert'}`,
            attachments: [{
                color: this.getSeverityColor(alert.severity),
                fields: [
                    { title: 'Severity', value: alert.severity, short: true },
                    { title: 'Source', value: alert.source || 'camel_router', short: true },
                    { title: 'Timestamp', value: new Date().toISOString(), short: false }
                ]
            }]
        });

        return this.sendWebhookPayload(config.slackWebhook, payload);
    }

    async sendEmail(alert) {
        // Email sending would require additional setup (SMTP, etc.)
        // For now, we'll log and return success
        console.log(`📧 Email alert would be sent: ${alert.message}`);
        return { channel: 'email', status: 'simulated' };
    }

    getSeverityColor(severity) {
        const colors = {
            critical: 'danger',
            high: 'warning',
            medium: 'warning',
            low: 'good'
        };
        return colors[severity] || 'warning';
    }

    generateAlertId(alert) {
        const hash = require('crypto')
            .createHash('md5')
            .update(JSON.stringify(alert) + Date.now())
            .digest('hex');
        return hash.substring(0, 8);
    }

    scheduleEscalation(alert, alertResult, delay) {
        setTimeout(async () => {
            console.log(`⏰ Escalating alert after ${delay}s delay`);
            await this.deliverAlert(alert, alertResult);
        }, delay * 1000);
    }

    async sendWebhookPayload(url, payload) {
        return new Promise((resolve, reject) => {
            const urlObj = new URL(url);
            const options = {
                hostname: urlObj.hostname,
                port: urlObj.port || (urlObj.protocol === 'https:' ? 443 : 80),
                path: urlObj.pathname + urlObj.search,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Content-Length': Buffer.byteLength(payload)
                }
            };

            const client = urlObj.protocol === 'https:' ? https : http;
            const req = client.request(options, (res) => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    resolve({ status: 'success' });
                } else {
                    reject(new Error(`Request failed with status ${res.statusCode}`));
                }
            });

            req.on('error', reject);
            req.write(payload);
            req.end();
        });
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
        const engine = new AlertingEngine();

        const result = await engine.processAlerts(inputData);

        const output = {
            timestamp: new Date().toISOString(),
            processor: 'alerting_engine',
            configuration: {
                channels: config.alertChannels,
                escalation_rules: config.escalationRules
            },
            alerting_results: result
        };

        if (outputFile) {
            fs.writeFileSync(outputFile, JSON.stringify(output, null, 2));
        } else {
            console.log(JSON.stringify(output, null, 2));
        }

    } catch (error) {
        const errorOutput = {
            error: error.message,
            processor: 'alerting_engine',
            success: false
        };
        console.error(JSON.stringify(errorOutput, null, 2));
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = { AlertingEngine };