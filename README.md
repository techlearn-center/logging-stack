# Logging Stack

> **What you'll create:** Set up a centralized logging system using Loki, Promtail, and Grafana to collect, store, and search logs from applications.

---

## Why Centralized Logging Matters

### The Problem Without Centralized Logging

```
┌─────────────────────────────────────────────────────────────────┐
│  WITHOUT CENTRALIZED LOGGING                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  You: "There's an error somewhere..."                           │
│                                                                  │
│  $ ssh server1                                                  │
│  $ tail -f /var/log/app.log    # Nothing here...               │
│                                                                  │
│  $ ssh server2                                                  │
│  $ tail -f /var/log/app.log    # Nothing here either...        │
│                                                                  │
│  $ ssh server3                                                  │
│  $ grep "error" /var/log/app.log | head -100                   │
│  # Finally found it! But wait, which user was affected?        │
│  # Let me check server1 again for the user's other requests... │
│                                                                  │
│  2 hours later: Still piecing together what happened            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### The Solution With Centralized Logging

```
┌─────────────────────────────────────────────────────────────────┐
│  WITH CENTRALIZED LOGGING (Loki + Grafana)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  You: "There's an error somewhere..."                           │
│                                                                  │
│  Open Grafana → Explore → Loki                                  │
│                                                                  │
│  Query: {app="myapp"} |= "error"                                │
│                                                                  │
│  Results (in 2 seconds):                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 14:32:15 server2 ERROR Payment failed for user_123      │   │
│  │ 14:32:14 server2 INFO  Processing payment for user_123  │   │
│  │ 14:32:13 server1 INFO  User user_123 added item to cart │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Complete timeline across ALL servers in ONE place!             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Real-World Impact

| Scenario | Without Centralized Logs | With Centralized Logs |
|----------|-------------------------|----------------------|
| **Debug an error** | SSH into 10 servers, grep each one | One query shows all logs |
| **Find user's journey** | Impossible across servers | Filter by user_id instantly |
| **Incident timeline** | Manually correlate timestamps | Automatic timeline view |
| **Compliance audit** | "We don't have those logs anymore" | Retained and searchable |
| **Pattern detection** | Hope you notice something | Alerts on log patterns |

---

## Prerequisites

### What You Need Before Starting

| Requirement | How to Check | Install Guide |
|-------------|--------------|---------------|
| **Docker** | `docker --version` | [docker.com](https://docker.com) |
| **Docker Compose** | `docker-compose --version` | Included with Docker Desktop |
| **Git** | `git --version` | [git-scm.com](https://git-scm.com) |

### Recommended (Completed Before)

- **monitoring-stack** challenge (metrics with Prometheus/Grafana)
- Basic understanding of Docker containers
- Familiarity with log files (you've seen `/var/log/` before)

### You DON'T Need To Know

- ❌ How Loki works internally
- ❌ LogQL query language (we'll teach you!)
- ❌ How log shipping works
- ❌ Elasticsearch or the ELK stack

---

## What is This Challenge?

You're setting up the **Logs** pillar of observability:

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE THREE PILLARS                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📊 METRICS (monitoring-stack)                                  │
│     "What is happening?" - Numbers over time                    │
│     Tools: Prometheus, Grafana                                  │
│                                                                  │
│  📝 LOGS (this challenge) ◄── YOU ARE HERE                     │
│     "Why did it happen?" - Text records of events              │
│     Tools: Loki, Promtail, Grafana                             │
│                                                                  │
│  🔗 TRACES (distributed-tracing)                                │
│     "Where did it happen?" - Request flow across services      │
│     Tools: Jaeger, Zipkin                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### What You'll Build

| Component | What It Does | File to Configure |
|-----------|--------------|-------------------|
| **Loki** | Stores and indexes logs | `loki/loki-config.yml` |
| **Promtail** | Collects logs and sends to Loki | `promtail/promtail-config.yml` |
| **Grafana** | Visualizes and searches logs | `grafana/provisioning/` |
| **Sample App** | Generates logs to collect | `app/app.py` |

---

## Understanding the Architecture

### How Logs Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│              │     │              │     │              │     │              │
│  Your App    │────▶│   Promtail   │────▶│     Loki     │────▶│   Grafana    │
│              │     │              │     │              │     │              │
│ Writes logs  │     │ Reads logs   │     │ Stores logs  │     │ Search/View  │
│ to stdout    │     │ Adds labels  │     │ Indexes them │     │ logs         │
│              │     │ Ships to Loki│     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

### Why Loki Instead of ELK?

| Feature | ELK (Elasticsearch) | Loki |
|---------|--------------------|----- |
| **Resource Usage** | Heavy (needs lots of RAM) | Lightweight |
| **Learning Curve** | Steep | Simple |
| **Cost** | Expensive at scale | Much cheaper |
| **Indexing** | Full-text indexing | Label-based indexing |
| **Query Language** | Complex DSL | LogQL (similar to PromQL) |
| **Grafana Integration** | Separate tool (Kibana) | Native |

**Loki's Philosophy:** "Like Prometheus, but for logs"
- Index metadata (labels), not log content
- Much more efficient storage
- Perfect for cloud-native applications

### Other Logging Tools Comparison

| Tool | Best For | Pros | Cons |
|------|----------|------|------|
| **Loki** | Cloud-native, Kubernetes | Lightweight, Grafana native | Less powerful search |
| **ELK Stack** | Enterprise, full-text search | Powerful, mature | Resource heavy, complex |
| **Splunk** | Enterprise, compliance | Very powerful | Very expensive |
| **Fluentd/Fluent Bit** | Log shipping | Flexible, many plugins | Just shipping, not storage |
| **CloudWatch Logs** | AWS native | Managed, integrated | Vendor lock-in |
| **Datadog Logs** | Full observability | All-in-one | Expensive |

---

## Quick Start

```bash
# 1. Fork this repo to your GitHub account

# 2. Clone YOUR fork
git clone https://github.com/YOUR-USERNAME/logging-stack.git
cd logging-stack

# 3. Complete the configuration files (see steps below)

# 4. Start the stack
docker-compose up -d

# 5. View logs in Grafana
# Open http://localhost:3000 (admin/admin)

# 6. Push and check your score
git push origin main
```

---

## Step 0: Understand Log Levels

> ⏱️ **Time:** 5 minutes (reading)

Before we start, understand the standard log levels:

| Level | When to Use | Example |
|-------|-------------|---------|
| **DEBUG** | Detailed info for debugging | `DEBUG: Variable x = 42` |
| **INFO** | Normal operations | `INFO: User logged in` |
| **WARNING** | Something unexpected but handled | `WARNING: Retry attempt 2 of 3` |
| **ERROR** | Something failed | `ERROR: Database connection failed` |
| **CRITICAL** | System is unusable | `CRITICAL: Out of disk space` |

```
Verbosity: DEBUG > INFO > WARNING > ERROR > CRITICAL

Production typically shows: INFO and above
Development shows: DEBUG and above
```

---

## Step 1: Configure Loki

> ⏱️ **Time:** 15-20 minutes

### What is Loki?

**Loki** is a log aggregation system. Think of it as a database specifically designed for logs:
- Receives logs from collectors (like Promtail)
- Stores them efficiently
- Allows fast searching by labels

### Your Task

Complete `loki/loki-config.yml`:

**Requirements:**
- [ ] Configure authentication (disabled for local dev)
- [ ] Set up storage (filesystem for local)
- [ ] Configure retention (7 days)
- [ ] Set up the schema config

<details>
<summary>💡 Hint 1: Basic Structure</summary>

```yaml
auth_enabled: false

server:
  http_listen_port: 3100

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory
```

</details>

<details>
<summary>💡 Hint 2: Schema Config</summary>

```yaml
schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h
```

</details>

<details>
<summary>🎯 Full Solution</summary>

```yaml
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    instance_addr: 127.0.0.1
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

ruler:
  alertmanager_url: http://localhost:9093

limits_config:
  retention_period: 168h  # 7 days
```

</details>

---

## Step 2: Configure Promtail

> ⏱️ **Time:** 20-25 minutes

### What is Promtail?

**Promtail** is the log collector. It:
- Watches log files or Docker containers
- Adds labels (metadata) to logs
- Ships logs to Loki

Think of Promtail as a delivery truck that picks up logs and delivers them to the Loki warehouse.

### How Promtail Labels Work

Labels are key-value pairs that help you filter logs:

```yaml
# Without labels - hard to find anything
{job="varlogs"}

# With labels - easy to filter
{job="app", env="production", service="payment", level="error"}
```

### Your Task

Complete `promtail/promtail-config.yml`:

**Requirements:**
- [ ] Configure Loki endpoint (where to send logs)
- [ ] Set up job to scrape Docker container logs
- [ ] Add labels for job name, container name
- [ ] Configure pipeline stages to extract log level

<details>
<summary>💡 Hint 1: Basic Structure</summary>

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: containers
    # ... docker config here
```

</details>

<details>
<summary>💡 Hint 2: Docker Log Scraping</summary>

```yaml
scrape_configs:
  - job_name: containers
    static_configs:
      - targets:
          - localhost
        labels:
          job: containerlogs
          __path__: /var/lib/docker/containers/*/*.log
    pipeline_stages:
      - json:
          expressions:
            output: log
            stream: stream
            attrs:
      - json:
          expressions:
            tag:
          source: attrs
      - regex:
          expression: (?P<container_name>(?:[^|]*[^|]))
          source: tag
      - labels:
          container_name:
```

</details>

<details>
<summary>🎯 Full Solution</summary>

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  # Scrape Docker container logs
  - job_name: containers
    static_configs:
      - targets:
          - localhost
        labels:
          job: containerlogs
          __path__: /var/lib/docker/containers/*/*.log

    pipeline_stages:
      # Parse Docker JSON log format
      - json:
          expressions:
            output: log
            stream: stream
            attrs:

      # Extract container name from attrs
      - json:
          expressions:
            tag:
          source: attrs

      # Parse container name
      - regex:
          expression: (?P<container_name>(?:[^|]*[^|]))
          source: tag

      # Add container_name as label
      - labels:
          container_name:
          stream:

      # Extract log level from log line
      - regex:
          expression: '(?P<level>(DEBUG|INFO|WARNING|ERROR|CRITICAL))'
          source: output

      - labels:
          level:

      # Use the actual log content
      - output:
          source: output
```

</details>

---

## Step 3: Configure Grafana Data Source

> ⏱️ **Time:** 10-15 minutes

### Your Task

Create `grafana/provisioning/datasources/loki.yml`:

**Requirements:**
- [ ] Add Loki as a data source
- [ ] Set the correct URL
- [ ] Make it the default for logs

<details>
<summary>🎯 Full Solution</summary>

```yaml
apiVersion: 1

datasources:
  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    isDefault: true
    editable: false
    jsonData:
      maxLines: 1000
```

</details>

---

## Step 4: Create a Sample Application

> ⏱️ **Time:** 20-25 minutes

### Your Task

Create an application that generates realistic logs. Complete `app/app.py`:

**Requirements:**
- [ ] Log at different levels (DEBUG, INFO, WARNING, ERROR)
- [ ] Include structured data (user_id, request_id, etc.)
- [ ] Simulate realistic scenarios (successful requests, failures, slow operations)

<details>
<summary>💡 Hint: Python Logging Setup</summary>

```python
import logging
import random
import time
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
```

</details>

<details>
<summary>🎯 Full Solution</summary>

```python
#!/usr/bin/env python3
"""
Sample application that generates realistic logs for the logging challenge.
"""

import logging
import random
import time
import json
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('webapp')

# Simulated users
USERS = ['user_123', 'user_456', 'user_789', 'user_admin', 'user_guest']

# Simulated endpoints
ENDPOINTS = [
    ('GET', '/api/users', 'users'),
    ('GET', '/api/products', 'products'),
    ('POST', '/api/orders', 'orders'),
    ('GET', '/api/health', 'health'),
    ('POST', '/api/payment', 'payment'),
    ('GET', '/api/search', 'search'),
]

def generate_request_id():
    """Generate a unique request ID."""
    return str(uuid.uuid4())[:8]

def simulate_request():
    """Simulate a single HTTP request with logging."""
    method, path, service = random.choice(ENDPOINTS)
    user_id = random.choice(USERS)
    request_id = generate_request_id()

    # Log request start
    logger.info(f"request_id={request_id} user={user_id} method={method} path={path} status=started")

    # Simulate processing time
    processing_time = random.uniform(0.01, 0.5)

    # Randomly generate different scenarios
    scenario = random.random()

    if scenario < 0.7:  # 70% success
        time.sleep(processing_time)
        status_code = 200
        logger.info(f"request_id={request_id} user={user_id} method={method} path={path} status={status_code} duration={processing_time:.3f}s")

    elif scenario < 0.85:  # 15% slow request
        slow_time = random.uniform(1.0, 3.0)
        time.sleep(0.1)  # Don't actually wait
        logger.warning(f"request_id={request_id} user={user_id} method={method} path={path} status=slow duration={slow_time:.3f}s threshold=1.0s")
        logger.info(f"request_id={request_id} user={user_id} method={method} path={path} status=200 duration={slow_time:.3f}s")

    elif scenario < 0.95:  # 10% client error
        status_code = random.choice([400, 401, 403, 404])
        error_messages = {
            400: "Bad request: missing required field 'email'",
            401: "Unauthorized: invalid or expired token",
            403: "Forbidden: insufficient permissions",
            404: f"Not found: resource at {path} does not exist"
        }
        logger.warning(f"request_id={request_id} user={user_id} method={method} path={path} status={status_code} error=\"{error_messages[status_code]}\"")

    else:  # 5% server error
        status_code = random.choice([500, 502, 503])
        error_messages = {
            500: "Internal server error: database connection failed",
            502: "Bad gateway: upstream service unavailable",
            503: "Service unavailable: server overloaded"
        }
        logger.error(f"request_id={request_id} user={user_id} method={method} path={path} status={status_code} error=\"{error_messages[status_code]}\"")

        # Log stack trace for 500 errors
        if status_code == 500:
            logger.debug(f"request_id={request_id} Stack trace: DatabaseError at line 42 in db.py")

def simulate_background_jobs():
    """Simulate background job logging."""
    jobs = ['email_sender', 'report_generator', 'data_sync', 'cleanup']
    job = random.choice(jobs)
    job_id = generate_request_id()

    scenario = random.random()

    if scenario < 0.9:  # 90% success
        logger.info(f"job={job} job_id={job_id} status=started")
        logger.info(f"job={job} job_id={job_id} status=completed items_processed={random.randint(10, 1000)}")
    else:  # 10% failure
        logger.info(f"job={job} job_id={job_id} status=started")
        logger.error(f"job={job} job_id={job_id} status=failed error=\"Connection timeout after 30s\"")

def simulate_system_events():
    """Simulate system-level logging."""
    events = [
        ("INFO", "Health check passed"),
        ("INFO", f"Active connections: {random.randint(10, 100)}"),
        ("INFO", f"Memory usage: {random.randint(40, 80)}%"),
        ("DEBUG", f"Cache hit ratio: {random.uniform(0.8, 0.99):.2%}"),
        ("WARNING", f"Connection pool near limit: {random.randint(80, 95)}% used"),
    ]

    level, message = random.choice(events)
    if level == "DEBUG":
        logger.debug(message)
    elif level == "INFO":
        logger.info(message)
    elif level == "WARNING":
        logger.warning(message)

def main():
    """Main loop to generate continuous logs."""
    logger.info("Application started - logging challenge demo")
    logger.info(f"Environment: development")
    logger.info(f"Version: 1.0.0")

    while True:
        # Weighted random choice of what to log
        action = random.choices(
            ['request', 'job', 'system'],
            weights=[70, 15, 15]
        )[0]

        if action == 'request':
            simulate_request()
        elif action == 'job':
            simulate_background_jobs()
        else:
            simulate_system_events()

        # Random delay between events
        time.sleep(random.uniform(0.5, 2.0))

if __name__ == '__main__':
    main()
```

</details>

Also create `app/requirements.txt`:

```
# No external dependencies needed - using standard library only
```

And `app/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY app.py .

CMD ["python", "-u", "app.py"]
```

---

## Step 5: Create Docker Compose

> ⏱️ **Time:** 15-20 minutes

### Your Task

Complete `docker-compose.yml`:

<details>
<summary>🎯 Full Solution</summary>

```yaml
version: "3.8"

services:
  # Log storage and query engine
  loki:
    image: grafana/loki:2.9.0
    container_name: loki
    ports:
      - "3100:3100"
    volumes:
      - ./loki/loki-config.yml:/etc/loki/local-config.yaml
      - loki-data:/loki
    command: -config.file=/etc/loki/local-config.yaml
    networks:
      - logging

  # Log collector
  promtail:
    image: grafana/promtail:2.9.0
    container_name: promtail
    volumes:
      - ./promtail/promtail-config.yml:/etc/promtail/config.yml
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock
    command: -config.file=/etc/promtail/config.yml
    depends_on:
      - loki
    networks:
      - logging

  # Visualization
  grafana:
    image: grafana/grafana:10.0.0
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - ./grafana/provisioning:/etc/grafana/provisioning
      - ./grafana/dashboards:/var/lib/grafana/dashboards
      - grafana-data:/var/lib/grafana
    depends_on:
      - loki
    networks:
      - logging

  # Sample application that generates logs
  app:
    build:
      context: ./app
    container_name: sample-app
    labels:
      - "logging=true"
    depends_on:
      - loki
    networks:
      - logging

volumes:
  loki-data:
  grafana-data:

networks:
  logging:
    driver: bridge
```

</details>

---

## Step 6: Create a Grafana Dashboard

> ⏱️ **Time:** 25-30 minutes

### LogQL Basics

LogQL is Loki's query language. It's similar to PromQL:

```logql
# Basic query - all logs from a job
{job="containerlogs"}

# Filter by container
{container_name="sample-app"}

# Search for text
{job="containerlogs"} |= "error"

# Case-insensitive search
{job="containerlogs"} |~ "(?i)error"

# Exclude text
{job="containerlogs"} != "health"

# Parse and filter
{job="containerlogs"} | json | level="ERROR"

# Count errors over time
count_over_time({job="containerlogs"} |= "ERROR" [5m])
```

### Your Task

Create `grafana/dashboards/logs-dashboard.json` with:
- [ ] Log volume over time
- [ ] Error rate panel
- [ ] Recent logs panel
- [ ] Log level distribution

Also create `grafana/provisioning/dashboards/dashboards.yml`:

```yaml
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    folderUid: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    options:
      path: /var/lib/grafana/dashboards
```

<details>
<summary>🎯 Dashboard JSON Solution</summary>

```json
{
  "annotations": {
    "list": []
  },
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "id": null,
  "links": [],
  "liveNow": false,
  "panels": [
    {
      "datasource": {
        "type": "loki",
        "uid": "loki"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "bars",
            "fillOpacity": 50,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "never",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "normal"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              }
            ]
          },
          "unit": "short"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 0
      },
      "id": 1,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "mode": "single",
          "sort": "none"
        }
      },
      "targets": [
        {
          "datasource": {
            "type": "loki",
            "uid": "loki"
          },
          "expr": "sum(count_over_time({job=\"containerlogs\"} [1m])) by (container_name)",
          "legendFormat": "{{container_name}}",
          "refId": "A"
        }
      ],
      "title": "Log Volume by Container",
      "type": "timeseries"
    },
    {
      "datasource": {
        "type": "loki",
        "uid": "loki"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              }
            ]
          }
        },
        "overrides": [
          {
            "matcher": {
              "id": "byName",
              "options": "ERROR"
            },
            "properties": [
              {
                "id": "color",
                "value": {
                  "fixedColor": "red",
                  "mode": "fixed"
                }
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "WARNING"
            },
            "properties": [
              {
                "id": "color",
                "value": {
                  "fixedColor": "orange",
                  "mode": "fixed"
                }
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "INFO"
            },
            "properties": [
              {
                "id": "color",
                "value": {
                  "fixedColor": "green",
                  "mode": "fixed"
                }
              }
            ]
          }
        ]
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 12,
        "y": 0
      },
      "id": 2,
      "options": {
        "displayLabels": [
          "name",
          "percent"
        ],
        "legend": {
          "displayMode": "table",
          "placement": "right",
          "showLegend": true
        },
        "pieType": "pie",
        "reduceOptions": {
          "calcs": [
            "lastNotNull"
          ],
          "fields": "",
          "values": false
        },
        "tooltip": {
          "mode": "single",
          "sort": "none"
        }
      },
      "targets": [
        {
          "datasource": {
            "type": "loki",
            "uid": "loki"
          },
          "expr": "sum(count_over_time({job=\"containerlogs\"} |~ \"(INFO|WARNING|ERROR|DEBUG)\" [1h])) by (level)",
          "legendFormat": "{{level}}",
          "refId": "A"
        }
      ],
      "title": "Log Level Distribution",
      "type": "piechart"
    },
    {
      "datasource": {
        "type": "loki",
        "uid": "loki"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "thresholds"
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "yellow",
                "value": 5
              },
              {
                "color": "red",
                "value": 10
              }
            ]
          },
          "unit": "short"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 4,
        "w": 6,
        "x": 0,
        "y": 8
      },
      "id": 3,
      "options": {
        "colorMode": "value",
        "graphMode": "area",
        "justifyMode": "auto",
        "orientation": "auto",
        "reduceOptions": {
          "calcs": [
            "lastNotNull"
          ],
          "fields": "",
          "values": false
        },
        "textMode": "auto"
      },
      "targets": [
        {
          "datasource": {
            "type": "loki",
            "uid": "loki"
          },
          "expr": "sum(count_over_time({job=\"containerlogs\"} |= \"ERROR\" [5m]))",
          "refId": "A"
        }
      ],
      "title": "Errors (last 5m)",
      "type": "stat"
    },
    {
      "datasource": {
        "type": "loki",
        "uid": "loki"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "thresholds"
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              }
            ]
          },
          "unit": "short"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 4,
        "w": 6,
        "x": 6,
        "y": 8
      },
      "id": 4,
      "options": {
        "colorMode": "value",
        "graphMode": "area",
        "justifyMode": "auto",
        "orientation": "auto",
        "reduceOptions": {
          "calcs": [
            "lastNotNull"
          ],
          "fields": "",
          "values": false
        },
        "textMode": "auto"
      },
      "targets": [
        {
          "datasource": {
            "type": "loki",
            "uid": "loki"
          },
          "expr": "sum(count_over_time({job=\"containerlogs\"} |= \"WARNING\" [5m]))",
          "refId": "A"
        }
      ],
      "title": "Warnings (last 5m)",
      "type": "stat"
    },
    {
      "datasource": {
        "type": "loki",
        "uid": "loki"
      },
      "gridPos": {
        "h": 12,
        "w": 24,
        "x": 0,
        "y": 12
      },
      "id": 5,
      "options": {
        "dedupStrategy": "none",
        "enableLogDetails": true,
        "prettifyLogMessage": false,
        "showCommonLabels": false,
        "showLabels": false,
        "showTime": true,
        "sortOrder": "Descending",
        "wrapLogMessage": false
      },
      "targets": [
        {
          "datasource": {
            "type": "loki",
            "uid": "loki"
          },
          "expr": "{job=\"containerlogs\"}",
          "refId": "A"
        }
      ],
      "title": "Recent Logs",
      "type": "logs"
    }
  ],
  "refresh": "5s",
  "schemaVersion": 38,
  "style": "dark",
  "tags": [
    "logging",
    "loki"
  ],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-15m",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "",
  "title": "Logging Dashboard",
  "uid": "logging-dashboard",
  "version": 1,
  "weekStart": ""
}
```

</details>

---

## Step 7: Test Your Stack

### Start Everything

```bash
docker-compose up -d
```

### Verify Services

```bash
# Check all containers are running
docker-compose ps

# Check Loki is responding
curl http://localhost:3100/ready

# Check Promtail is running
docker logs promtail

# Check app is generating logs
docker logs sample-app
```

### Access Grafana

1. Open http://localhost:3000
2. Login: admin / admin
3. Go to **Explore** (compass icon)
4. Select **Loki** as data source
5. Run query: `{job="containerlogs"}`

### Try These LogQL Queries

```logql
# All logs from sample app
{container_name="sample-app"}

# Only errors
{container_name="sample-app"} |= "ERROR"

# Find specific user
{container_name="sample-app"} |= "user_123"

# Errors with request ID
{container_name="sample-app"} |= "ERROR" | json | request_id != ""

# Count errors per minute
count_over_time({container_name="sample-app"} |= "ERROR" [1m])

# Slow requests
{container_name="sample-app"} |= "slow"
```

---

## Step 8: Run Progress Checker

```bash
python run.py
```

**Expected output when complete:**
```
============================================================
  📝 Logging Stack Challenge
============================================================

  ✅ Loki Config (20/20 points)
  ✅ Promtail Config (25/25 points)
  ✅ Grafana Datasource (15/15 points)
  ✅ Grafana Dashboard (20/20 points)
  ✅ Docker Compose (20/20 points)

============================================================
  🎯 Total Score: 100/100
  🎉 CHALLENGE COMPLETE!
============================================================
```

---

## LogQL Cheat Sheet

### Basic Queries

```logql
# Select by label
{job="containerlogs"}
{container_name="myapp"}
{job="containerlogs", level="ERROR"}

# Label matching operators
{job="containerlogs"}              # Exact match
{job=~"container.*"}               # Regex match
{job!="varlogs"}                   # Not equal
{job!~"temp.*"}                    # Not regex match
```

### Filter Expressions

```logql
# Line contains
{job="containerlogs"} |= "error"

# Line doesn't contain
{job="containerlogs"} != "health"

# Regex match
{job="containerlogs"} |~ "(?i)error"

# Regex doesn't match
{job="containerlogs"} !~ "debug"
```

### Parsing

```logql
# JSON parsing
{job="containerlogs"} | json

# Extract specific fields
{job="containerlogs"} | json | user_id="123"

# Regex extraction
{job="containerlogs"} | regexp "user=(?P<user>\\w+)"

# Logfmt parsing
{job="containerlogs"} | logfmt
```

### Aggregations

```logql
# Count logs over time
count_over_time({job="containerlogs"} [5m])

# Rate of logs
rate({job="containerlogs"} [5m])

# Sum by label
sum by (level) (count_over_time({job="containerlogs"} [5m]))

# Top 5 by log count
topk(5, sum by (container_name) (count_over_time({job="containerlogs"} [1h])))
```

---

## Understanding Logging (For DevOps Students)

### What Makes Good Logs

| Good Log | Bad Log |
|----------|---------|
| `2024-01-15 14:32:15 INFO user=123 action=login status=success ip=192.168.1.1` | `Login worked` |
| `ERROR request_id=abc123 service=payment error="Card declined" user_id=456` | `Error occurred` |
| `DEBUG query="SELECT * FROM users WHERE id=?" params=[123] duration=0.045s` | `Query ran` |

### Log Levels in Practice

```
Production:
  INFO  ████████████████████ 80%
  WARN  ████                 15%
  ERROR █                     5%

If you see:
  ERROR ████████████████████ - Something is very wrong!
  DEBUG ████████████████████ - Turn down logging level!
```

### Structured vs Unstructured Logs

```
# Unstructured (hard to parse)
User john logged in from 192.168.1.1 at 2024-01-15 14:32:15

# Structured (easy to parse and query)
{"timestamp": "2024-01-15T14:32:15Z", "level": "INFO", "user": "john", "action": "login", "ip": "192.168.1.1"}

# Key-value (also good)
timestamp=2024-01-15T14:32:15Z level=INFO user=john action=login ip=192.168.1.1
```

### What You Can Say in Interviews

> "I set up centralized logging using Loki, Promtail, and Grafana. Promtail collects logs from Docker containers, adds metadata labels, and ships them to Loki. Loki stores logs efficiently using label-based indexing rather than full-text indexing, which keeps costs low. I created Grafana dashboards to visualize log patterns and set up alerts for error rate thresholds. I chose Loki over ELK because of its lower resource requirements and native Grafana integration."

---

## Troubleshooting

<details>
<summary>❌ Loki not receiving logs</summary>

1. Check Promtail can reach Loki:
   ```bash
   docker exec promtail wget -qO- http://loki:3100/ready
   ```
2. Check Promtail logs: `docker logs promtail`
3. Verify the Loki URL in promtail-config.yml

</details>

<details>
<summary>❌ No logs in Grafana</summary>

1. Check Loki has data:
   ```bash
   curl 'http://localhost:3100/loki/api/v1/labels'
   ```
2. Verify data source URL in Grafana
3. Check time range (top right in Grafana)

</details>

<details>
<summary>❌ Docker permission errors on Linux</summary>

Promtail needs access to Docker socket:
```bash
sudo chmod 666 /var/run/docker.sock
```

Or run with sudo: `sudo docker-compose up -d`

</details>

<details>
<summary>❌ Windows: Can't access Docker socket</summary>

On Windows, the Docker socket path is different. Update `docker-compose.yml`:
```yaml
volumes:
  - //var/run/docker.sock:/var/run/docker.sock
```

Or use Docker Desktop's WSL2 backend.

</details>

---

## What You Learned

- ✅ **Centralized Logging** - Why it matters
- ✅ **Loki** - Log storage and querying
- ✅ **Promtail** - Log collection and labeling
- ✅ **LogQL** - Query language for logs
- ✅ **Grafana** - Log visualization
- ✅ **Structured Logging** - Best practices

---

## Next Steps

| Challenge | What You'll Learn |
|-----------|-------------------|
| **[distributed-tracing](https://github.com/techlearn-center/distributed-tracing)** | Jaeger for request tracing across microservices |
| **[monitoring-stack](https://github.com/techlearn-center/monitoring-stack)** | If you haven't done it yet - Prometheus metrics |

### Complete Observability

After completing all three challenges, you'll have:

```
┌─────────────────────────────────────────────────────────────────┐
│                   YOUR OBSERVABILITY STACK                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Problem: "The payment service is slow"                         │
│                                                                  │
│  📊 METRICS: Prometheus shows latency spike at 14:32           │
│  📝 LOGS: Loki shows "database timeout" errors                 │
│  🔗 TRACES: Jaeger shows slow query in payment → db call       │
│                                                                  │
│  Root Cause: Database connection pool exhausted                 │
│  Fix: Increase pool size, add connection recycling             │
│  Time to Resolution: 15 minutes (not 4 hours!)                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

Good luck! 📝
