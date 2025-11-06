# Multi-stage build for CAS Bridge

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Set labels
LABEL maintainer="your.email@example.com"
LABEL description="CAS Bridge - Symbolic Math Operations Service"
LABEL version="1.0.0"

# Create non-root user for security
RUN useradd -m -u 1000 casuser && \
    mkdir -p /app && \
    chown -R casuser:casuser /app

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/casuser/.local

# Copy application code
COPY --chown=casuser:casuser app/ ./app/
COPY --chown=casuser:casuser ui/ ./ui/
COPY --chown=casuser:casuser openapi/ ./openapi/

# Switch to non-root user
USER casuser

# Add local Python packages to PATH
ENV PATH=/home/casuser/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz')" || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
