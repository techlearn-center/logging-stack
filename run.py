#!/usr/bin/env python3
"""
Logging Stack Challenge - Progress Checker
==========================================
This script checks your progress through the logging challenge.
Run it anytime to see what you've completed and what's left to do.

Usage:
    python run.py          # Check all tasks
    python run.py --task 1 # Check specific task
"""

import subprocess
import sys
import yaml
import json
import time
import os
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header():
    """Print the challenge header."""
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}  📊 Logging Stack Challenge - Progress Checker{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")

def print_task(num, name, status, message=""):
    """Print task status."""
    if status == "pass":
        icon = "✅"
        color = Colors.GREEN
    elif status == "fail":
        icon = "❌"
        color = Colors.RED
    else:
        icon = "⏳"
        color = Colors.YELLOW

    print(f"{icon} {Colors.BOLD}Task {num}:{Colors.END} {name}")
    if message:
        print(f"   {color}{message}{Colors.END}")

def check_file_exists(filepath):
    """Check if a file exists."""
    return Path(filepath).exists()

def load_yaml_file(filepath):
    """Load and parse a YAML file."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            # Remove comments and check if there's actual content
            lines = [l for l in content.split('\n') if l.strip() and not l.strip().startswith('#')]
            if not lines:
                return None
            return yaml.safe_load(content)
    except Exception as e:
        return None

def check_docker_running():
    """Check if Docker is running."""
    try:
        result = subprocess.run(
            ['docker', 'info'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except:
        return False

def check_container_running(container_name):
    """Check if a specific container is running."""
    try:
        result = subprocess.run(
            ['docker', 'ps', '--filter', f'name={container_name}', '--format', '{{.Names}}'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return container_name in result.stdout
    except:
        return False

def check_loki_healthy():
    """Check if Loki is responding."""
    try:
        import urllib.request
        req = urllib.request.urlopen('http://localhost:3100/ready', timeout=5)
        return req.status == 200
    except:
        return False

def check_grafana_healthy():
    """Check if Grafana is responding."""
    try:
        import urllib.request
        req = urllib.request.urlopen('http://localhost:3000/api/health', timeout=5)
        return req.status == 200
    except:
        return False

def check_loki_has_logs():
    """Check if Loki has received any logs."""
    try:
        import urllib.request
        import json
        url = 'http://localhost:3100/loki/api/v1/query?query={job="docker"}'
        req = urllib.request.urlopen(url, timeout=5)
        data = json.loads(req.read().decode())
        return len(data.get('data', {}).get('result', [])) > 0
    except:
        return False

def check_task_1_loki_config():
    """Check Task 1: Loki configuration."""
    filepath = 'loki/loki-config.yml'

    if not check_file_exists(filepath):
        return False, "File not found: loki/loki-config.yml"

    config = load_yaml_file(filepath)
    if config is None:
        return False, "Config file is empty or only has comments - uncomment and configure it!"

    # Check required sections
    required_sections = ['auth_enabled', 'server', 'common', 'schema_config', 'storage_config']
    missing = [s for s in required_sections if s not in config]

    if missing:
        return False, f"Missing sections: {', '.join(missing)}"

    # Check server configuration
    if 'server' in config:
        if config['server'].get('http_listen_port') != 3100:
            return False, "Server should listen on port 3100"

    return True, "Loki configuration looks good!"

def check_task_2_promtail_config():
    """Check Task 2: Promtail configuration."""
    filepath = 'promtail/promtail-config.yml'

    if not check_file_exists(filepath):
        return False, "File not found: promtail/promtail-config.yml"

    config = load_yaml_file(filepath)
    if config is None:
        return False, "Config file is empty or only has comments - uncomment and configure it!"

    # Check required sections
    required_sections = ['server', 'positions', 'clients', 'scrape_configs']
    missing = [s for s in required_sections if s not in config]

    if missing:
        return False, f"Missing sections: {', '.join(missing)}"

    # Check client URL points to Loki
    if 'clients' in config and config['clients']:
        client_url = config['clients'][0].get('url', '')
        if 'loki' not in client_url and '3100' not in client_url:
            return False, "Client URL should point to Loki (e.g., http://loki:3100/loki/api/v1/push)"

    # Check scrape configs exist
    if 'scrape_configs' in config:
        if not config['scrape_configs']:
            return False, "No scrape configs defined - add at least one!"

    return True, "Promtail configuration looks good!"

def check_task_3_grafana_datasource():
    """Check Task 3: Grafana data source configuration."""
    filepath = 'grafana/provisioning/datasources/loki.yml'

    if not check_file_exists(filepath):
        return False, "File not found: grafana/provisioning/datasources/loki.yml"

    config = load_yaml_file(filepath)
    if config is None:
        return False, "Config file is empty or only has comments - uncomment and configure it!"

    # Check datasources exist
    if 'datasources' not in config or not config['datasources']:
        return False, "No datasources defined"

    # Check Loki datasource
    loki_ds = None
    for ds in config['datasources']:
        if ds.get('type') == 'loki':
            loki_ds = ds
            break

    if not loki_ds:
        return False, "No Loki datasource found - type should be 'loki'"

    # Check URL
    url = loki_ds.get('url', '')
    if 'loki' not in url and '3100' not in url:
        return False, "Datasource URL should point to Loki"

    return True, "Grafana datasource configuration looks good!"

def check_task_4_stack_running():
    """Check Task 4: Stack is running."""
    if not check_docker_running():
        return False, "Docker is not running"

    containers = ['loki', 'promtail', 'grafana']
    not_running = []

    for container in containers:
        if not check_container_running(container):
            not_running.append(container)

    if not_running:
        return False, f"Containers not running: {', '.join(not_running)}"

    # Check health endpoints
    if not check_loki_healthy():
        return False, "Loki is not responding - check logs with: docker logs loki"

    if not check_grafana_healthy():
        return False, "Grafana is not responding - check logs with: docker logs grafana"

    return True, "All services are running and healthy!"

def check_task_5_logs_flowing():
    """Check Task 5: Logs are flowing to Loki."""
    if not check_loki_healthy():
        return False, "Loki is not running - complete Task 4 first"

    if not check_loki_has_logs():
        return False, "No logs found in Loki yet - wait a moment and try again"

    return True, "Logs are flowing to Loki! Open Grafana to explore them."

def main():
    """Main function to run all checks."""
    print_header()

    results = []
    total_points = 0
    earned_points = 0

    # Task definitions
    tasks = [
        (1, "Configure Loki", check_task_1_loki_config, 20),
        (2, "Configure Promtail", check_task_2_promtail_config, 25),
        (3, "Configure Grafana Data Source", check_task_3_grafana_datasource, 15),
        (4, "Start the Stack", check_task_4_stack_running, 20),
        (5, "Logs Flowing to Loki", check_task_5_logs_flowing, 20),
    ]

    # Check specific task if requested
    specific_task = None
    if len(sys.argv) > 2 and sys.argv[1] == '--task':
        try:
            specific_task = int(sys.argv[2])
        except ValueError:
            print(f"{Colors.RED}Invalid task number{Colors.END}")
            sys.exit(1)

    for num, name, check_func, points in tasks:
        if specific_task and num != specific_task:
            continue

        total_points += points
        try:
            passed, message = check_func()
            if passed:
                earned_points += points
                print_task(num, name, "pass", message)
            else:
                print_task(num, name, "fail", message)
        except Exception as e:
            print_task(num, name, "fail", f"Error checking: {str(e)}")
        print()

    # Print summary
    print(f"{Colors.CYAN}{'='*60}{Colors.END}")
    percentage = (earned_points / total_points * 100) if total_points > 0 else 0

    if percentage >= 70:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 Congratulations! You passed the challenge!{Colors.END}")
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}Keep going! You're making progress.{Colors.END}")

    print(f"\n{Colors.BOLD}Score:{Colors.END} {earned_points}/{total_points} points ({percentage:.0f}%)")
    print(f"{Colors.BOLD}Passing Score:{Colors.END} 70%")

    if percentage < 100:
        print(f"\n{Colors.BLUE}💡 Hints:{Colors.END}")
        print("  • Check the README.md for detailed instructions")
        print("  • Use 'docker-compose logs <service>' to debug issues")
        print("  • Grafana is available at http://localhost:3000")
        print("  • Loki API is available at http://localhost:3100")

    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}\n")

    return 0 if percentage >= 70 else 1

if __name__ == '__main__':
    sys.exit(main())
