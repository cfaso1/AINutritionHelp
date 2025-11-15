# Use official Python runtime as base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p backend/uploads logs

# Expose the port (Render uses 10000)
EXPOSE 10000

# Set environment variables
ENV FLASK_ENV=production \
    FLASK_DEBUG=0 \
    HOST=0.0.0.0 \
    PYTHONUNBUFFERED=1

# Install Gunicorn for production
RUN pip install gunicorn

# Run the application with Gunicorn
# Optimized for Render free tier cold starts:
# - Single worker (faster startup, less memory)
# - Preload app (app loads before worker forks)
# - 200s timeout (handles slow cold starts)
# - 4 threads per worker (handles concurrent requests)
CMD gunicorn --bind 0.0.0.0:$PORT \
    --workers 1 \
    --threads 4 \
    --timeout 200 \
    --graceful-timeout 200 \
    --keep-alive 5 \
    --preload \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    backend.api:app
