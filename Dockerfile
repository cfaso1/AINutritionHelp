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

# Expose the port the app runs on
EXPOSE 5000

# Set environment variables
ENV FLASK_ENV=production \
    FLASK_DEBUG=0 \
    HOST=0.0.0.0 \
    PORT=5000 \
    PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "run.py"]
