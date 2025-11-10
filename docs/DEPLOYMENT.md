# Production Deployment Guide

## 🌐 Live Application

**Frontend (Netlify):** https://balancebotai.netlify.app/
**Backend API (Render):** https://balancebotapi.onrender.com/
**Health Check:** https://balancebotapi.onrender.com/api/health

---

## 📋 Prerequisites

### Required Accounts
- GitHub account (for version control)
- Netlify account (for frontend hosting)
- Render account (for backend hosting)
- Google Cloud account (for Gemini API)

### Required API Keys
1. **Google Gemini API Key**
   - Visit: https://aistudio.google.com/apikey
   - Create API key
   - Keep it secure - you'll need it for deployment

2. **Secret Key for Flask**
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

---

## 🚀 Deployment Steps

### 1. Backend Deployment (Render)

**Option A: Using Blueprint (Recommended)**

1. Push code to GitHub
2. Go to https://dashboard.render.com
3. Click **New** → **Blueprint**
4. Connect your GitHub repository
5. Render will detect `render.yaml` and create the service automatically
6. Add environment variables in the Render dashboard:

**Required Environment Variables:**
```bash
GOOGLE_API_KEY=your_gemini_api_key
SECRET_KEY=your_generated_secret_key
ALLOWED_ORIGINS=https://balancebotai.netlify.app
```

**Option B: Manual Setup**

1. Go to https://dashboard.render.com
2. Click **New** → **Web Service**
3. Connect GitHub repository
4. Configure:
   - **Name:** balancebot-api
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python run.py`
5. Add environment variables (same as above)

**Verify Deployment:**
```bash
curl https://balancebotapi.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "AI Nutrition Help API",
  "version": "2.0.0",
  "environment": "production"
}
```

### 2. Frontend Deployment (Netlify)

1. Go to https://app.netlify.com
2. Click **Add new site** → **Import an existing project**
3. Connect to your GitHub repository
4. Configure:
   - **Branch:** main
   - **Build command:** (leave empty)
   - **Publish directory:** frontend
5. Click **Deploy site**

**Custom Domain (Optional):**
1. Go to **Site settings** → **Domain management**
2. Click **Add custom domain**
3. Follow Netlify's DNS configuration instructions

### 3. Update CORS Configuration

After frontend deploys:

1. Copy your Netlify URL (e.g., `https://balancebotai.netlify.app`)
2. Go to Render dashboard → Your service → **Environment**
3. Update `ALLOWED_ORIGINS` to your Netlify URL
4. Save (service will auto-redeploy)

---

## 🔍 Verification Checklist

- [ ] Backend health endpoint returns status "healthy"
- [ ] Frontend loads without errors
- [ ] Can register new user account
- [ ] Can login successfully
- [ ] Can update profile settings
- [ ] Can scan/upload nutrition facts
- [ ] AI evaluation works (check API quota)
- [ ] Chat functionality works
- [ ] No CORS errors in browser console

---

## 📊 Monitoring

### Render Dashboard
- **Logs:** Real-time backend logs
- **Metrics:** CPU, memory, request count
- **Events:** Deployment history

### Netlify Dashboard
- **Deploy logs:** Frontend build status
- **Analytics:** Traffic and performance
- **Functions:** (Not used in this project)

### Browser Console
- Press F12 → Console tab
- Should see: `🍎 NutriScan initialized in production mode`
- Should see: `API URL: https://balancebotapi.onrender.com/api`

---

## 🐛 Common Issues

### CORS Errors
**Symptom:** "Access-Control-Allow-Origin" error

**Fix:**
1. Verify `ALLOWED_ORIGINS` in Render matches your Netlify URL exactly
2. No trailing slash in the URL
3. Restart Render service if needed

### API Quota Exceeded
**Symptom:** "I've reached my daily API usage limit"

**Fix:**
1. Check usage: https://ai.dev/usage?tab=rate-limit
2. Generate new API key or wait for reset (24 hours)
3. Consider enabling billing for higher limits

### Backend Cold Start
**Symptom:** First request takes 30+ seconds

**Fix:**
- Render free tier sleeps after 15 min inactivity
- Upgrade to Starter plan ($7/mo) for 24/7 uptime

### Configuration Errors
**Symptom:** Backend won't start, validation errors

**Fix:**
1. Check Render logs for specific error
2. Verify all required environment variables are set
3. Ensure SECRET_KEY and GOOGLE_API_KEY are not placeholders

---

## 🔄 Updating Production

### Code Changes
```bash
git add .
git commit -m "Your change description"
git push origin main
```

Both Render and Netlify will auto-deploy on push to main branch.

**Deploy Times:**
- Netlify: ~30-60 seconds
- Render: ~2-3 minutes

### Environment Variable Changes
1. Update in Render dashboard → Environment tab
2. Service auto-restarts
3. Check logs to verify changes

---

## 📈 Scaling Considerations

### Free Tier Limits
- **Netlify:** 100GB bandwidth/month, unlimited builds
- **Render:** 750 hours/month, sleeps after 15 min
- **Google Gemini:** 1,500 requests/day (free tier)

### Upgrade Options
- **Render Starter:** $7/mo for 24/7 uptime
- **Render Standard:** $25/mo for better performance
- **Google Gemini Paid:** ~$0.001/request, higher quotas

---

## 🔐 Security Best Practices

- ✅ All secrets in environment variables (not in code)
- ✅ CORS restricted to frontend domain only
- ✅ Rate limiting enabled
- ✅ HTTPS enforced
- ✅ Security headers configured
- ✅ Input validation on all endpoints
- ✅ Authentication required for sensitive routes

---

## 📞 Support

**Check Logs First:**
- Render: Dashboard → Logs tab
- Netlify: Deploys → Deploy details → Deploy log
- Browser: F12 → Console tab

**Common Log Locations:**
- Backend startup: First ~20 lines of Render logs
- API errors: Search logs for "ERROR" or "WARN"
- Frontend errors: Browser console (F12)

---

**Last Updated:** November 2025
**Status:** ✅ Production Ready
