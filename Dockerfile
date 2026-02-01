# Multi-stage Dockerfile for EACP
# Stage 1: Build dependencies
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    chromium-browser \
    chromium-codecs-ffmpeg \
    ffmpeg \
    poppler-utils \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Set environment variables
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV EACP_ENV=production

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 eacp && chown -R eacp:eacp /app
USER eacp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)"

# Default command
CMD ["python", "main.py"]

# Expose API port
EXPOSE 8000

# Labels
LABEL maintainer="EACP Team"
LABEL version="1.0"
LABEL description="Enterprise Agent Collaboration Platform - Multi-modal LLM Agents with MLOps"
