#!/usr/bin/env python3
"""
Sample application that generates realistic logs for the logging challenge.
This simulates a web application with various log levels and scenarios.
"""

import logging
import random
import time
import uuid
from datetime import datetime

# Configure logging with structured format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('webapp')

# Simulated users
USERS = ['user_123', 'user_456', 'user_789', 'user_admin', 'user_guest', 'user_new', 'user_premium']

# Simulated endpoints
ENDPOINTS = [
    ('GET', '/api/users', 'users'),
    ('GET', '/api/products', 'products'),
    ('POST', '/api/orders', 'orders'),
    ('GET', '/api/health', 'health'),
    ('POST', '/api/payment', 'payment'),
    ('GET', '/api/search', 'search'),
    ('PUT', '/api/profile', 'profile'),
    ('DELETE', '/api/cart', 'cart'),
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

    if scenario < 0.70:  # 70% success
        time.sleep(processing_time)
        status_code = 200
        logger.info(f"request_id={request_id} user={user_id} method={method} path={path} status={status_code} duration={processing_time:.3f}s")

    elif scenario < 0.85:  # 15% slow request
        slow_time = random.uniform(1.0, 3.0)
        time.sleep(0.1)  # Don't actually wait that long
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

        # Log additional debug info for 500 errors
        if status_code == 500:
            logger.debug(f"request_id={request_id} stack_trace=\"DatabaseError at line 42 in db.py -> ConnectionPool.get()\"")


def simulate_background_jobs():
    """Simulate background job logging."""
    jobs = ['email_sender', 'report_generator', 'data_sync', 'cache_cleanup', 'notification_worker']
    job = random.choice(jobs)
    job_id = generate_request_id()

    scenario = random.random()

    if scenario < 0.85:  # 85% success
        items = random.randint(10, 1000)
        duration = random.uniform(0.5, 5.0)
        logger.info(f"job={job} job_id={job_id} status=started")
        logger.debug(f"job={job} job_id={job_id} processing items={items}")
        logger.info(f"job={job} job_id={job_id} status=completed items_processed={items} duration={duration:.2f}s")
    elif scenario < 0.95:  # 10% warning
        logger.info(f"job={job} job_id={job_id} status=started")
        logger.warning(f"job={job} job_id={job_id} status=completed_with_warnings warnings=\"Some items skipped due to validation\"")
    else:  # 5% failure
        logger.info(f"job={job} job_id={job_id} status=started")
        logger.error(f"job={job} job_id={job_id} status=failed error=\"Connection timeout after 30s\"")


def simulate_system_events():
    """Simulate system-level logging."""
    events = [
        ("INFO", f"Health check passed - all services healthy"),
        ("INFO", f"Active connections: {random.randint(10, 100)}"),
        ("INFO", f"Memory usage: {random.randint(40, 80)}%"),
        ("INFO", f"CPU usage: {random.randint(10, 60)}%"),
        ("DEBUG", f"Cache hit ratio: {random.uniform(0.8, 0.99):.2%}"),
        ("DEBUG", f"Database pool: {random.randint(5, 20)} active connections"),
        ("WARNING", f"Connection pool usage high: {random.randint(80, 95)}%"),
        ("WARNING", f"Slow query detected: SELECT * FROM orders took {random.uniform(1.0, 3.0):.2f}s"),
    ]

    level, message = random.choice(events)
    if level == "DEBUG":
        logger.debug(message)
    elif level == "INFO":
        logger.info(message)
    elif level == "WARNING":
        logger.warning(message)


def simulate_security_events():
    """Simulate security-related logging."""
    events = [
        ("INFO", f"Login successful user=user_{random.randint(100, 999)} ip=192.168.1.{random.randint(1, 254)}"),
        ("WARNING", f"Failed login attempt user=unknown ip=10.0.0.{random.randint(1, 254)} reason=\"invalid credentials\""),
        ("WARNING", f"Rate limit exceeded ip=172.16.0.{random.randint(1, 254)} endpoint=/api/search"),
        ("INFO", f"Password changed user=user_{random.randint(100, 999)}"),
        ("WARNING", f"Suspicious activity detected ip=203.0.113.{random.randint(1, 254)} pattern=\"multiple 404s\""),
    ]

    level, message = random.choice(events)
    if level == "INFO":
        logger.info(message)
    elif level == "WARNING":
        logger.warning(message)


def main():
    """Main loop to generate continuous logs."""
    logger.info("=" * 60)
    logger.info("Application started - Logging Challenge Demo")
    logger.info("=" * 60)
    logger.info(f"Environment: development")
    logger.info(f"Version: 1.0.0")
    logger.info(f"Log level: DEBUG")
    logger.info("Generating sample logs for the logging-stack challenge...")
    logger.info("=" * 60)

    iteration = 0
    while True:
        iteration += 1

        # Weighted random choice of what to log
        action = random.choices(
            ['request', 'job', 'system', 'security'],
            weights=[60, 15, 15, 10]
        )[0]

        if action == 'request':
            simulate_request()
        elif action == 'job':
            simulate_background_jobs()
        elif action == 'system':
            simulate_system_events()
        else:
            simulate_security_events()

        # Periodic health log
        if iteration % 50 == 0:
            logger.info(f"Heartbeat: iteration={iteration} uptime={iteration * 1.5:.0f}s")

        # Random delay between events (0.5 to 2 seconds)
        time.sleep(random.uniform(0.5, 2.0))


if __name__ == '__main__':
    main()
