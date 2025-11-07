# AI Nutrition Help - Production Deployment Guide

This guide will help you deploy the AI Nutrition Help application to production.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Local Development](#local-development)
- [Production Deployment](#production-deployment)
- [Security Checklist](#security-checklist)
- [Monitoring and Maintenance](#monitoring-and-maintenance)

## Prerequisites

### Required Software

- Python 3.12+
- Docker & Docker Compose (for containerized deployment)
- Tesseract OCR (for local development without Docker)
- Node.js (optional, for serving frontend separately)

### Required Accounts & Keys

1. **Google AI API Key**
   - Get it from: https://aistudio.google.com/apikey
   - Used for the AI nutrition evaluation features

## Environment Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd AINutritionHelp
```

### 2. Create Environment Configuration

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```bash
# REQUIRED: Google AI Configuration
GOOGLE_API_KEY=your_google_api_key_here

# REQUIRED IN PRODUCTION: Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=<generate-a-secure-secret-key>

# Server Configuration
HOST=0.0.0.0
PORT=5000

# Frontend Configuration
FRONTEND_URL=https://yourdomain.com

# CORS Configuration (comma-separated)
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Database Configuration
DATABASE_PATH=backend/nutrition_app.db

# Upload Configuration
UPLOAD_FOLDER=backend/uploads
MAX_UPLOAD_SIZE_MB=16

# Rate Limiting
RATE_LIMIT_ENABLED=1
RATE_LIMIT_PER_MINUTE=60

# Logging
LOG_LEVEL=INFO
LOG_FILE=app.log
```

### 3. Generate a Secure Secret Key

```python
# Run this in Python
import secrets
print(secrets.token_hex(32))
```

Copy the output and use it as your `SECRET_KEY` in `.env`.

### 4. Install Dependencies

#### Option A: Using Virtual Environment (Recommended for Local Development)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Option B: Using Docker (Recommended for Production)

No additional installation needed - Docker handles everything.

## Local Development

### Without Docker

1. Install Tesseract OCR:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr

   # macOS
   brew install tesseract

   # Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   ```

2. Activate virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. Run the application:
   ```bash
   python run.py
   ```

4. Open frontend:
   - Open `frontend/index.html` in your browser
   - Or use a simple HTTP server:
     ```bash
     cd frontend
     python -m http.server 3000
     ```
   - Navigate to http://localhost:3000

### With Docker

```bash
docker-compose up --build
```

Access the application at http://localhost

## Production Deployment

### Option 1: Docker Compose (Recommended)

This is the simplest production deployment method.

1. **Set up your server** (Ubuntu 22.04+ recommended)

2. **Install Docker and Docker Compose**:
   ```bash
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh

   # Install Docker Compose
   sudo apt-get install docker-compose-plugin
   ```

3. **Clone repository and configure**:
   ```bash
   git clone <your-repo-url>
   cd AINutritionHelp
   cp .env.example .env
   # Edit .env with your production values
   nano .env
   ```

4. **Update frontend API URL**:
   Edit `frontend/config.js` to set your production API URL:
   ```javascript
   production: {
       API_URL: 'https://yourdomain.com/api',
       DEBUG: false
   }
   ```

5. **Build and run**:
   ```bash
   # Run with nginx (full production setup)
   docker-compose --profile production up -d --build

   # Or run without nginx (API only)
   docker-compose up -d --build
   ```

6. **Set up SSL** (recommended):
   ```bash
   # Install certbot
   sudo apt-get install certbot

   # Get certificate
   sudo certbot certonly --standalone -d yourdomain.com

   # Copy certificates
   sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
   sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem

   # Update nginx.conf to enable HTTPS (uncomment the HTTPS server block)
   nano nginx/nginx.conf

   # Restart nginx
   docker-compose restart nginx
   ```

### Option 2: Manual Deployment (VPS/Cloud)

1. **Set up server** (Ubuntu 22.04+)

2. **Install dependencies**:
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3.12 python3-pip python3-venv tesseract-ocr nginx
   ```

3. **Set up application**:
   ```bash
   cd /var/www
   git clone <your-repo-url> nutriscan
   cd nutriscan
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with production values
   ```

4. **Set up systemd service**:

   Create `/etc/systemd/system/nutriscan.service`:
   ```ini
   [Unit]
   Description=AI Nutrition Help API
   After=network.target

   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/var/www/nutriscan
   Environment="PATH=/var/www/nutriscan/venv/bin"
   ExecStart=/var/www/nutriscan/venv/bin/python run.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start:
   ```bash
   sudo systemctl enable nutriscan
   sudo systemctl start nutriscan
   ```

5. **Configure Nginx**:
   ```bash
   sudo cp nginx/nginx.conf /etc/nginx/sites-available/nutriscan
   sudo ln -s /etc/nginx/sites-available/nutriscan /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### Option 3: Cloud Platforms

#### Heroku

1. Create `Procfile`:
   ```
   web: python run.py
   ```

2. Deploy:
   ```bash
   heroku create your-app-name
   heroku config:set GOOGLE_API_KEY=your_key
   heroku config:set SECRET_KEY=your_secret
   git push heroku main
   ```

#### AWS/Google Cloud/Azure

Use the Dockerfile provided for containerized deployment on these platforms.

## Security Checklist

Before deploying to production, ensure:

- [ ] **API Keys Secured**
  - ✓ `.env` file is not committed to git (in `.gitignore`)
  - ✓ Google API key has been rotated from the demo version
  - ✓ `SECRET_KEY` is generated and unique

- [ ] **Authentication**
  - ✓ JWT authentication is enabled
  - ✓ Demo user credentials removed from code
  - ✓ Password minimum length enforced (8+ characters)

- [ ] **CORS Configuration**
  - ✓ `ALLOWED_ORIGINS` set to your production domains only
  - ✓ No `localhost` origins in production

- [ ] **Security Headers**
  - ✓ Security headers enabled in Flask
  - ✓ HTTPS enabled (SSL certificate installed)

- [ ] **Rate Limiting**
  - ✓ Rate limiting enabled
  - ✓ Configured appropriately for expected traffic

- [ ] **Debug Mode**
  - ✓ `FLASK_DEBUG=0` in production
  - ✓ Error details not exposed to users

- [ ] **File Uploads**
  - ✓ File size limits enforced
  - ✓ File type validation enabled
  - ✓ Upload directory permissions correct

## Monitoring and Maintenance

### Check Application Health

```bash
curl https://yourdomain.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "AI Nutrition Help API",
  "version": "2.0.0",
  "environment": "production",
  "timestamp": "2025-01-06T..."
}
```

### View Logs

#### Docker Deployment
```bash
# API logs
docker-compose logs -f api

# Nginx logs
docker-compose logs -f nginx
```

#### Manual Deployment
```bash
# Application logs
tail -f app.log

# Systemd logs
sudo journalctl -u nutriscan -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Database Backup

```bash
# Backup database
cp backend/nutrition_app.db backup/nutrition_app_$(date +%Y%m%d).db

# Or with Docker
docker-compose exec api cp /app/backend/nutrition_app.db /app/backup/
```

### Update Deployment

```bash
# Pull latest changes
git pull

# Rebuild and restart (Docker)
docker-compose up -d --build

# Or restart service (Manual)
sudo systemctl restart nutriscan
```

### SSL Certificate Renewal

```bash
# Renew certificate (certbot)
sudo certbot renew

# Copy renewed certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem

# Restart nginx
docker-compose restart nginx
```

## Troubleshooting

### Application Won't Start

1. Check environment variables:
   ```bash
   python -c "from config import active_config; active_config.validate()"
   ```

2. Check logs for errors

3. Verify all dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```

### Authentication Errors

1. Verify `SECRET_KEY` is set
2. Check token expiration (default 24 hours)
3. Clear browser localStorage and re-login

### Database Errors

1. Check database file permissions
2. Ensure `backend/` directory is writable
3. Run migrations:
   ```python
   from backend.database import migrate_database
   migrate_database()
   ```

### OCR Not Working

1. Verify Tesseract is installed:
   ```bash
   tesseract --version
   ```

2. Check supported file types
3. Verify file size is under limit

## Support

For issues and questions:
- Check the main README.md
- Review application logs
- Check GitHub issues

## License

[Your License Here]
