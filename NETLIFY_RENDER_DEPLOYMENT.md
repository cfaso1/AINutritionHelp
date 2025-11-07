# Deployment Guide: Netlify (Frontend) + Render (Backend)

This guide walks you through deploying your AI Nutrition Help application with:
- **Frontend**: Netlify (static hosting)
- **Backend**: Render (Python/Flask API)

---

## Prerequisites

1. **GitHub Account** (for code repository)
2. **Netlify Account** (free tier works) - https://netlify.com
3. **Render Account** (free tier works) - https://render.com
4. **Google AI API Key** - https://aistudio.google.com/apikey

---

## Part 1: Prepare Your Code

### 1. Update Frontend Configuration

Edit `frontend/config.js` and set your Render backend URL:

```javascript
production: {
    // Replace with your actual Render URL (you'll get this after backend deployment)
    API_URL: 'https://your-backend-app.onrender.com/api',
    DEBUG: false
}
```

**Note**: You'll update this after deploying the backend in Part 2.

### 2. Commit and Push to GitHub

```bash
git add .
git commit -m "Prepare for Netlify + Render deployment"
git push origin main
```

---

## Part 2: Deploy Backend to Render

### Step 1: Create a New Web Service

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select your `AINutritionHelp` repository

### Step 2: Configure the Service

Fill in the following settings:

| Field | Value |
|-------|-------|
| **Name** | `balancebot-api` (or your preferred name) |
| **Region** | Choose closest to your users |
| **Branch** | `main` |
| **Root Directory** | Leave empty |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python run.py` |
| **Instance Type** | `Free` (or paid for better performance) |

### Step 3: Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** and add these:

```bash
# Required
GOOGLE_API_KEY=your_google_api_key_here
SECRET_KEY=<generate-with-python-secrets>
FLASK_ENV=production
FLASK_DEBUG=0

# Server Configuration
HOST=0.0.0.0
PORT=10000

# CORS - UPDATE THIS after deploying frontend to Netlify
ALLOWED_ORIGINS=https://your-site.netlify.app

# Database
DATABASE_PATH=backend/nutrition_app.db

# Optional
RATE_LIMIT_ENABLED=1
RATE_LIMIT_PER_MINUTE=60
LOG_LEVEL=INFO
```

**To generate SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Step 4: Deploy

1. Click **"Create Web Service"**
2. Wait for the build to complete (5-10 minutes)
3. **Copy your backend URL**: `https://your-backend-app.onrender.com`

### Step 5: Test Backend

Once deployed, test it:
```bash
curl https://your-backend-app.onrender.com/api/health
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

---

## Part 3: Deploy Frontend to Netlify

### Step 1: Update Frontend with Backend URL

1. Edit `frontend/config.js`
2. Replace the production API_URL with your Render backend URL:

```javascript
production: {
    API_URL: 'https://your-backend-app.onrender.com/api',  // ← Use your actual Render URL
    DEBUG: false
}
```

3. Commit and push:
```bash
git add frontend/config.js
git commit -m "Update production API URL"
git push origin main
```

### Step 2: Deploy to Netlify

#### Option A: Netlify UI (Easiest)

1. Go to https://app.netlify.com
2. Click **"Add new site"** → **"Import an existing project"**
3. Connect to GitHub and select your repository
4. Configure:
   - **Branch**: `main`
   - **Base directory**: Leave empty
   - **Build command**: Leave empty
   - **Publish directory**: `frontend`
5. Click **"Deploy site"**

#### Option B: Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Initialize and deploy
cd /path/to/AINutritionHelp
netlify init
netlify deploy --prod
```

### Step 3: Get Your Frontend URL

After deployment, Netlify will give you a URL like:
- `https://random-name-12345.netlify.app`

You can customize this:
1. Go to **Site settings** → **Domain management**
2. Click **"Change site name"**
3. Choose something like: `balancebot.netlify.app`

---

## Part 4: Update CORS Settings

Now that you have your Netlify URL, update the backend's CORS settings:

1. Go to your Render dashboard
2. Select your backend service
3. Go to **Environment** tab
4. Update `ALLOWED_ORIGINS`:
   ```
   https://balancebot.netlify.app
   ```

   If you have a custom domain:
   ```
   https://balancebot.netlify.app,https://yourdomain.com
   ```

5. Click **"Save Changes"**
6. Render will automatically redeploy

---

## Part 5: Test Your Deployment

### 1. Visit Your Site
Open `https://your-site.netlify.app`

### 2. Test User Flow
1. ✅ Click **"Sign Up"** and create an account
2. ✅ Complete the profile setup
3. ✅ Upload a nutrition label image
4. ✅ Get AI analysis
5. ✅ Test the chat feature

### 3. Check for Errors
- Open browser DevTools (F12)
- Check Console for errors
- Check Network tab for failed requests

---

## Common Issues & Solutions

### Issue 1: CORS Errors

**Error**: `Access to fetch at 'https://...' from origin 'https://...' has been blocked by CORS`

**Solution**:
1. Check Render environment variable `ALLOWED_ORIGINS`
2. Make sure it includes your exact Netlify URL (with `https://`)
3. No trailing slashes
4. Save and wait for Render to redeploy

### Issue 2: 404 on Backend

**Error**: `GET https://your-backend.onrender.com/api/... 404`

**Solution**:
1. Verify backend is deployed and running
2. Check Render logs: Dashboard → Your Service → Logs
3. Verify the API endpoint exists (check backend/api.py)

### Issue 3: Database Errors on Render

**Error**: Database file errors or "read-only filesystem"

**Solution**:
Render's free tier has ephemeral storage. For production:
1. Upgrade to paid tier with persistent disk
2. Or use a hosted database (PostgreSQL recommended)

### Issue 4: Tesseract OCR Not Found

**Solution**:
Add a `render.yaml` file to install Tesseract:

```yaml
services:
  - type: web
    name: balancebot-api
    env: python
    buildCommand: |
      apt-get update
      apt-get install -y tesseract-ocr
      pip install -r requirements.txt
    startCommand: python run.py
```

Then use this instead of manual web service creation.

### Issue 5: Frontend Shows Old API URL

**Solution**:
1. Hard refresh: `Ctrl + Shift + R`
2. Clear browser cache
3. Check Network tab to see actual requests

---

## Production Optimization

### 1. Custom Domain (Optional)

**For Netlify:**
1. Go to **Domain settings**
2. Click **"Add custom domain"**
3. Follow DNS setup instructions

**For Render:**
1. Go to **Settings** → **Custom Domain**
2. Add your domain (e.g., `api.yourdomain.com`)
3. Update DNS records

### 2. Environment Variables Best Practices

Store sensitive values in environment variables:
- ✅ `GOOGLE_API_KEY`
- ✅ `SECRET_KEY`
- ❌ Never commit these to git

### 3. Monitoring

**Render Logs:**
```bash
# View real-time logs
Dashboard → Your Service → Logs
```

**Netlify Logs:**
```bash
# View deployment logs
Dashboard → Your Site → Deploys → [Latest] → Deploy log
```

### 4. Rate Limiting

Free tier limitations:
- **Render**: Service sleeps after 15 min inactivity (first request takes ~30s)
- **Netlify**: 100 GB bandwidth/month, 300 build minutes/month

Consider upgrading for production use.

---

## Update Checklist

Before going live:

- [ ] ✅ Backend deployed to Render
- [ ] ✅ Frontend deployed to Netlify
- [ ] ✅ `GOOGLE_API_KEY` set in Render environment
- [ ] ✅ `SECRET_KEY` generated and set
- [ ] ✅ `ALLOWED_ORIGINS` updated with Netlify URL
- [ ] ✅ Frontend `config.js` updated with Render API URL
- [ ] ✅ Test signup/login works
- [ ] ✅ Test OCR upload works
- [ ] ✅ Test AI analysis works
- [ ] ✅ Test chat feature works
- [ ] ✅ No CORS errors in browser console

---

## Maintenance

### Deploy Updates

**Backend (Render):**
1. Push code to GitHub
2. Render auto-deploys on push (if enabled)
3. Or manually: Dashboard → Your Service → Manual Deploy

**Frontend (Netlify):**
1. Push code to GitHub
2. Netlify auto-deploys on push
3. Or manually: Dashboard → Your Site → Deploys → Trigger deploy

### Database Backup

Since Render free tier is ephemeral, consider:
1. Upgrading to persistent disk
2. Regular exports via API
3. Using PostgreSQL instead of SQLite

---

## Cost Estimate

| Service | Free Tier | Paid Tier |
|---------|-----------|-----------|
| **Render** | ✅ Free (with limitations) | $7/month (persistent storage) |
| **Netlify** | ✅ Free (100GB bandwidth) | $19/month (Pro) |
| **Google AI API** | ✅ Free tier available | Pay per request |

**Total**: $0-26/month depending on needs

---

## Support

If you encounter issues:
1. Check Render logs for backend errors
2. Check browser console for frontend errors
3. Verify environment variables are set correctly
4. Test API endpoints with curl/Postman

---

## Next Steps

Once deployed:
1. Share your Netlify URL with users
2. Monitor usage and errors
3. Consider custom domain
4. Set up analytics (optional)
5. Configure email notifications for errors

---

**Your deployment URLs:**
- Frontend: `https://your-site.netlify.app`
- Backend API: `https://your-backend-app.onrender.com`
- Health Check: `https://your-backend-app.onrender.com/api/health`

🎉 **Congratulations on deploying your app!**
