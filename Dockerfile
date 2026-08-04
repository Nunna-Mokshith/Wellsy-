# Wellsy AI Assistant — Docker Image
# Multi-Agent Jarvis-class AI with Solar System UI

FROM python:3.13-slim

# System dependencies for numpy, audio processing, and general build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libsndfile1 \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for Docker layer caching
COPY requirements-docker.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend and frontend source code
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Create necessary directories
RUN mkdir -p /app/storage /app/voice_cache /app/backend/db

# Expose the Wellsy dashboard port
EXPOSE 8765

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8765/api/health || exit 1

# Environment defaults
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run Wellsy
CMD ["python", "backend/main.py"]
