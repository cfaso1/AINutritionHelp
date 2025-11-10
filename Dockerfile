# Use official Python runtime as base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Tesseract OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Verify Tesseract installation
RUN tesseract --version

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
    PYTHONUNBUFFERED=1 \
    TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# Run the application
CMD ["python", "run.py"]
