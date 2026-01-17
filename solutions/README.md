# Solutions - Logging Stack Challenge

> **Warning**: Only look at these solutions if you're stuck! Try to complete the challenge yourself first.

This folder contains complete solution files for reference.

## Solution Files

| File | Description |
|------|-------------|
| `loki-config.yml` | Complete Loki configuration |
| `promtail-config.yml` | Complete Promtail configuration |
| `grafana-datasource.yml` | Complete Grafana datasource configuration |

## How to Use Solutions

If you're stuck on a particular task:

1. First, re-read the README.md in the parent folder
2. Try to understand what the configuration should do
3. Look at the solution for hints, not to copy directly
4. Understand WHY the solution works

## Applying Solutions

To test with solutions (for debugging only):

```bash
# Copy solution files
cp solutions/loki-config.yml loki/loki-config.yml
cp solutions/promtail-config.yml promtail/promtail-config.yml
cp solutions/grafana-datasource.yml grafana/provisioning/datasources/loki.yml

# Start the stack
docker-compose up -d
```

## Key Learning Points

### Loki Configuration
- `auth_enabled: false` - Disables multi-tenancy for simplicity
- `server.http_listen_port: 3100` - Standard Loki port
- `common.storage.filesystem` - Uses local filesystem for storage
- `schema_config` - Defines how logs are indexed and stored

### Promtail Configuration
- `positions.filename` - Tracks reading progress (like a bookmark)
- `clients.url` - Where to send logs (Loki's push endpoint)
- `scrape_configs` - Defines what logs to collect
- `pipeline_stages` - How to parse and label logs

### Grafana Data Source
- `type: loki` - Tells Grafana this is a Loki datasource
- `url: http://loki:3100` - Uses Docker network name
- `access: proxy` - Grafana proxies requests to Loki
- `isDefault: true` - Makes Loki the default datasource

## Common Issues and Solutions

### Loki Not Starting
- Check YAML syntax (indentation matters!)
- Ensure all directories exist
- Check Docker logs: `docker logs loki`

### No Logs Appearing
- Verify Promtail can reach Loki
- Check Promtail logs: `docker logs promtail`
- Ensure log paths are correctly mounted

### Grafana Can't Connect
- Verify Loki is running and healthy
- Check URL uses Docker network name (`loki`, not `localhost`)
- Restart Grafana after config changes
