# Deployment Checklist - Netlify + Render

Use this checklist to ensure a smooth deployment process.

## Pre-Deployment

- [ ] Code is committed and pushed to GitHub
- [ ] `.env` file is in `.gitignore` (never commit secrets!)
- [ ] Google API Key obtained from https://aistudio.google.com/apikey
- [ ] Secret key generated: `python3 -c "import secrets; print(secrets.token_hex(32))"`

## Backend Deployment (Render)

- [ ] Created Render account
- [ ] Connected GitHub repository to Render
- [ ] Created new Web Service or used `render.yaml` blueprint
- [ ] Set environment variables:
  - [ ] `GOOGLE_API_KEY`
  - [ ] `SECRET_KEY`
  - [ ] `FLASK_ENV=production`
  - [ ] `ALLOWED_ORIGINS` (will update after frontend deployment)
- [ ] Backend deployed successfully
- [ ] Copied backend URL: `https://__________.onrender.com`
- [ ] Tested health endpoint: `curl https://your-backend.onrender.com/api/health`

## Frontend Configuration

- [ ] Updated `frontend/config.js` with Render backend URL:
  ```javascript
  API_URL: 'https://your-backend-app.onrender.com/api'
  ```
- [ ] Committed and pushed changes to GitHub

## Frontend Deployment (Netlify)

- [ ] Created Netlify account
- [ ] Connected GitHub repository to Netlify
- [ ] Configured deployment:
  - [ ] Branch: `main`
  - [ ] Publish directory: `frontend`
- [ ] Frontend deployed successfully
- [ ] Copied frontend URL: `https://__________.netlify.app`
- [ ] (Optional) Customized site name

## CORS Configuration Update

- [ ] Updated Render environment variable `ALLOWED_ORIGINS` with Netlify URL
- [ ] Format: `https://balancebotai.netlify.app` (no trailing slash)
- [ ] Render service redeployed automatically
- [ ] Waited for redeploy to complete (~2-3 minutes)

## Testing

- [ ] Opened frontend URL in browser
- [ ] Checked browser console for errors (F12)
- [ ] Tested user registration
- [ ] Tested login
- [ ] Completed profile setup
- [ ] Uploaded nutrition label image
- [ ] Verified OCR processing works
- [ ] Tested AI analysis
- [ ] Tested chat feature
- [ ] No CORS errors in console

## Post-Deployment

- [ ] Documented URLs:
  - Frontend: `https://__________.netlify.app`
  - Backend: `https://__________.onrender.com`
- [ ] Set up monitoring (optional)
- [ ] Configured custom domain (optional)
- [ ] Enabled auto-deploy on git push (should be default)

## Known Limitations (Free Tier)

- [ ] Aware: Render service sleeps after 15 min inactivity
- [ ] Aware: First request after sleep takes ~30 seconds
- [ ] Aware: Render free tier has ephemeral storage (database resets on redeploy)
- [ ] Aware: For production, consider upgrading to Render paid tier for:
  - Persistent disk
  - No sleep
  - Better performance

## Troubleshooting Done

If you encounter issues, check these:

- [ ] Verified backend is running (not sleeping)
- [ ] Checked Render logs for errors
- [ ] Verified CORS origins match exactly
- [ ] Tested API endpoints with curl
- [ ] Cleared browser cache
- [ ] Verified Google API key is valid
- [ ] Checked for typos in environment variables

## URLs Reference

**Production:**
- Frontend: `https://__________.netlify.app`
- Backend API: `https://__________.onrender.com/api`
- Health Check: `https://__________.onrender.com/api/health`

**Development:**
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:5000/api`
- Health Check: `http://localhost:5000/api/health`

---

## Quick Commands

**Generate Secret Key:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

**Test Backend Health:**
```bash
curl https://your-backend.onrender.com/api/health
```

**View Render Logs:**
```
Render Dashboard → Your Service → Logs
```

**Redeploy Backend:**
```
Render Dashboard → Your Service → Manual Deploy → Deploy latest commit
```

**Redeploy Frontend:**
```
Netlify Dashboard → Your Site → Deploys → Trigger deploy
```

---

✅ **Deployment Complete!**
Share your Netlify URL with users and start collecting feedback!
