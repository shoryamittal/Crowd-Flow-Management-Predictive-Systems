# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies for OpenCV and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

# Create a non-root user
RUN useradd -m -s /bin/bash sentinel_user

# Install runtime dependencies for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /home/sentinel_user/.local
ENV PATH=/home/sentinel_user/.local/bin:$PATH

# Copy application code
COPY . /app

# Change ownership of the app directory to the non-root user
RUN chown -R sentinel_user:sentinel_user /app

# Switch to non-root user
USER sentinel_user

# Default Cloud Run environment variables
ENV PORT=8080 \
    HOST=0.0.0.0 \
    PYTHONUNBUFFERED=1

# Expose container port (8080 for Cloud Run, 5000 for local)
EXPOSE 8080 5000

# Add liveness healthcheck using standard Python urllib
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import os, urllib.request; p = os.environ.get('PORT', '8080'); urllib.request.urlopen(f'http://localhost:{p}/health')" || exit 1

# Run the application
CMD ["python", "deploy.py"]
