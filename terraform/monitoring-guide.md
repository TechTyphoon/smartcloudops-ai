# Smart CloudOps AI - Monitoring Stack Guide

## 📊 Phase 1.2: Complete Monitoring Setup

This guide covers the complete monitoring stack setup including Prometheus, Grafana, and Node Exporter with automated dashboards and alerting.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐
│ EC2 Monitoring  │    │ EC2 Application │
│                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Prometheus  │◄┼────┼─┤ Node Export │ │
│ │   :9090     │ │    │ │   :9100     │ │
│ └─────────────┘ │    │ └─────────────┘ │
│                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │  Grafana    │ │    │ │ Flask App   │ │
│ │   :3001     │ │    │ │   :3000     │ │
│ └─────────────┘ │    │ └─────────────┘ │
│                 │    │                 │
│ ┌─────────────┐ │    │                 │
│ │ Node Export │ │    │                 │
│ │   :9100     │ │    │                 │
│ └─────────────┘ │    │                 │
└─────────────────┘    └─────────────────┘
```

## 🚀 Deployment Process

### 1. Deploy Infrastructure
```bash
cd terraform
terraform apply
```

### 2. Configure Monitoring
```bash
# Get the output IPs
MONITORING_IP=$(terraform output -raw monitoring_instance_public_ip)
APPLICATION_IP=$(terraform output -raw application_instance_public_ip)

# Configure the monitoring stack
./scripts/configure_monitoring.sh $MONITORING_IP $APPLICATION_IP
```

## 📈 Pre-configured Dashboards

### 1. System Overview Dashboard
- **CPU Usage**: Real-time and historical CPU utilization
- **Memory Usage**: RAM consumption with thresholds
- **Disk Usage**: Root filesystem utilization
- **Network Traffic**: RX/TX bytes per interface

### 2. Prometheus Monitoring Dashboard
- **Target Status**: Health of all monitored endpoints
- **Scrape Duration**: Performance of metric collection
- **TSDB Metrics**: Prometheus internal metrics
- **Flask App Metrics**: Request rate and duration

## 🚨 Alert Rules

The monitoring stack includes pre-configured alerts:

| Alert | Condition | Duration | Severity |
|-------|-----------|----------|----------|
| HighCPUUsage | CPU > 90% | 3 minutes | Critical |
| HighMemoryUsage | Memory > 95% | 2 minutes | Critical |
| HighDiskUsage | Disk > 85% | 5 minutes | Warning |
| InstanceDown | Target unreachable | 1 minute | Critical |
| FlaskAppDown | Flask app unreachable | 1 minute | Critical |
| HighRequestRate | Requests > 100/sec | 2 minutes | Warning |
| HighRequestDuration | 95th percentile > 1s | 3 minutes | Warning |

## 🔧 Monitoring Stack Components

### Prometheus Configuration
- **Scrape Interval**: 15 seconds (global), 5-10s (specific jobs)
- **Retention**: 200 hours
- **Targets**: Both EC2 instances + Flask application
- **Service Discovery**: EC2 auto-discovery for dynamic scaling

### Grafana Configuration
- **Default User**: admin/admin
- **Data Sources**: Prometheus (auto-configured)
- **Dashboards**: Auto-provisioned on startup
- **Plugins**: Clock panel, SimpleJSON datasource

### Node Exporter
- **Port**: 9100
- **Metrics**: System metrics (CPU, memory, disk, network)
- **Installation**: Both systemd service and Docker container

## 📊 Accessing Your Monitoring

After deployment, access these services:

```bash
# From Terraform outputs
terraform output

# Direct access
Prometheus: http://<monitoring-ip>:9090
Grafana:    http://<monitoring-ip>:3001
Flask App:  http://<application-ip>:3000
```

## 🔍 Troubleshooting

### Common Issues

1. **Grafana shows "No data"**
   ```bash
   # Check Prometheus targets
   curl http://<monitoring-ip>:9090/api/v1/targets
   
   # Verify data source
   curl -u admin:admin http://<monitoring-ip>:3001/api/datasources
   ```

2. **Targets are down**
   ```bash
   # Check Node Exporter
   curl http://<instance-ip>:9100/metrics
   
   # Check Flask app metrics
   curl http://<application-ip>:3000/metrics
   ```

3. **Dashboards not loading**
   ```bash
   # Check Grafana logs
   ssh ec2-user@<monitoring-ip>
   cd /opt/monitoring
   docker-compose logs grafana
   ```

### Verification Commands

```bash
# Check all containers are running
docker-compose ps

# View Prometheus configuration
curl http://localhost:9090/api/v1/status/config

# List Grafana dashboards
curl -u admin:admin http://localhost:3001/api/search
```

## 🔄 Maintenance

### Updating Dashboards
1. Modify JSON files in `terraform/configs/`
2. Re-run `terraform apply`
3. Restart Grafana container

### Adding New Targets
1. Update `prometheus.yml`
2. Use Prometheus web UI to reload config:
   ```bash
   curl -X POST http://<monitoring-ip>:9090/-/reload
   ```

### Backup and Recovery
```bash
# Backup Grafana data
docker cp grafana:/var/lib/grafana ./grafana-backup

# Backup Prometheus data
docker cp prometheus:/prometheus ./prometheus-backup
```

## 📈 Metrics Available

### System Metrics (Node Exporter)
- `node_cpu_seconds_total`: CPU time spent in different modes
- `node_memory_MemTotal_bytes`: Total memory
- `node_memory_MemAvailable_bytes`: Available memory
- `node_filesystem_size_bytes`: Filesystem size
- `node_filesystem_avail_bytes`: Available filesystem space
- `node_network_receive_bytes_total`: Network RX bytes
- `node_network_transmit_bytes_total`: Network TX bytes

### Application Metrics (Flask)
- `flask_requests_total`: Total HTTP requests
- `flask_request_duration_seconds`: Request duration histogram

## 🔜 Next Steps

Phase 1.2 is now complete! Ready for:
- **Phase 2**: Flask ChatOps Application Development
- **Phase 3**: ML Anomaly Detection Integration
- **Phase 4**: Auto-Remediation Logic

## 📚 References

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Node Exporter Metrics](https://github.com/prometheus/node_exporter)