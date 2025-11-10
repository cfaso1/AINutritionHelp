# Production Deployment Summary

## 🌐 Live URLs

### Frontend (Netlify)
**URL:** https://balancebotai.netlify.app/

### Backend API (Render)
**URL:** https://balancebotapi.onrender.com/

**Health Check:** https://balancebotapi.onrender.com/api/health

---

## ✅ Production Configuration

### Environment Variables (Set in Render Dashboard)

```bash
# Required Secrets (Set in Render)
GOOGLE_API_KEY=your_actual_key_here
SECRET_KEY=your_actual_secret_here

# Production Settings
FLASK_ENV=production
FLASK_DEBUG=0

# CORS Configuration
ALLOWED_ORIGINS=https://balancebotai.netlify.app

# Server Configuration
HOST=0.0.0.0
PORT=10000

# Database & Uploads
DATABASE_PATH=backend/nutrition_app.db
UPLOAD_FOLDER=backend/uploads
MAX_UPLOAD_SIZE_MB=16

# Rate Limiting
RATE_LIMIT_ENABLED=1
RATE_LIMIT_PER_MINUTE=60

# Logging
LOG_LEVEL=INFO
LOG_FILE=app.log
```

---

## 🔧 Configuration Files

### 1. Frontend Configuration (`frontend/config.js`)
```javascript
production: {
    API_URL: 'https://balancebotapi.onrender.com/api',
    DEBUG: false
}
```

### 2. Backend Configuration (`config/config.py`)
- Default FLASK_ENV: `production`
- Default ALLOWED_ORIGINS: `https://balancebotai.netlify.app`
- Production validation enabled
- Localhost detection with warnings

### 3. Deployment Files
- **Netlify:** `netlify.toml` (in root)
- **Render:** `render.yaml` (in root)
- **Python Version:** `runtime.txt` → `3.12`

---

## 🚀 Deployment Process

### Initial Deployment

1. **Backend (Render):**
   ```bash
   # Render automatically deploys from main branch
   # Blueprint: render.yaml
   # Build: pip install -r requirements.txt
   # Start: python run.py
   ```

2. **Frontend (Netlify):**
   ```bash
   # Netlify automatically deploys from main branch
   # Publish directory: frontend
   # No build command needed (static site)
   ```

### Updating Production

```bash
# Make changes locally
git add .
git commit -m "Your changes"
git push origin main

# Both services auto-deploy on push
# - Render: ~3-5 minutes
# - Netlify: ~30-60 seconds
```

---

## 🔍 Production Verification

### Backend Health Check
```bash
curl https://balancebotapi.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "AI Nutrition Help API",
  "version": "2.0.0",
  "environment": "production",
  "timestamp": "..."
}
```

### Frontend Console (F12)
```
🍎 NutriScan initialized in production mode
API URL: https://balancebotapi.onrender.com/api
```

### Run.py Startup Banner (Render Logs)
```
============================================================
  🚀 AI Nutrition Help API - PRODUCTION
============================================================
  Environment: production
  Server: http://0.0.0.0:10000
  Debug Mode: OFF ✅
  Rate Limiting: ON ✅
  CORS Origins: https://balancebotai.netlify.app
============================================================
```

---

## 🔒 Security Checklist

- [x] FLASK_DEBUG set to `0` (OFF)
- [x] SECRET_KEY is unique and not committed to repo
- [x] GOOGLE_API_KEY stored securely in Render dashboard
- [x] CORS limited to frontend domain only
- [x] Rate limiting enabled (60 requests/minute)
- [x] HTTPS enforced on both frontend and backend
- [x] Security headers configured in Netlify
- [x] No localhost URLs in production config

---

## 📊 Monitoring

### Render Dashboard
- **Build Logs:** Check deployment success
- **Runtime Logs:** Monitor API requests and errors
- **Metrics:** View CPU, memory, and request stats

### Netlify Dashboard
- **Deploy Logs:** Check frontend deployment
- **Analytics:** View page visits and performance
- **Forms:** Monitor any form submissions

### Browser Console
- Check for API connection errors
- Verify correct API URL is being used
- Monitor network requests (F12 → Network tab)

---

## 🐛 Troubleshooting

### CORS Errors
**Symptom:** "Access-Control-Allow-Origin" error in browser console

**Fix:**
1. Check ALLOWED_ORIGINS in Render dashboard
2. Ensure it matches: `https://balancebotai.netlify.app`
3. No trailing slash!
4. Restart Render service if needed

### API Connection Failed
**Symptom:** "Failed to fetch" or network errors

**Check:**
1. Backend health: https://balancebotapi.onrender.com/api/health
2. Render service is running (not sleeping on free tier)
3. frontend/config.js has correct API_URL
4. Browser console shows correct API URL

### Development Mode Warning
**Symptom:** Seeing "DEVELOPMENT" instead of "PRODUCTION" in logs

**Fix:**
1. Set `FLASK_ENV=production` in Render environment variables
2. Restart service
3. Check logs for "🚀 PRODUCTION" banner

---

## 📝 Maintenance

### Adding Environment Variables
1. Go to Render dashboard → Your service
2. Environment tab
3. Add/edit variables
4. Service auto-restarts

### Updating Dependencies
1. Edit `requirements.txt` locally
2. Commit and push
3. Render automatically rebuilds

### Database Backups
```bash
# The SQLite database persists on Render's disk
# Consider periodic exports for backup
```

---

## 🎯 Performance Notes

### Render Free Tier
- Service sleeps after 15 minutes of inactivity
- First request after sleep: ~30-60 seconds cold start
- Consider upgrading to Starter plan for 24/7 uptime

### Netlify
- Instant global CDN
- No cold starts
- Excellent performance

---

**Last Updated:** November 2025
**Status:** ✅ Production Ready
