# Dockerfile for Sample Logging Application
# ==========================================
# This builds a simple Python application that generates logs
# for Promtail to collect and send to Loki.

FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Run the application
CMD ["python", "-u", "app.py"]
