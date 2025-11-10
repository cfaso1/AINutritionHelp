# OCR Fix Guide

## Problem
OCR was extracting 0 characters on Render deployment because Tesseract wasn't installed. Render's free tier doesn't allow `apt-get` in build commands.

## Solution
Switched to Docker deployment which gives full control over system dependencies.

## Changes Made

### 1. Dockerfile
- ✅ Installs Tesseract OCR with English language pack
- ✅ Installs all OpenCV system dependencies
- ✅ Sets `TESSDATA_PREFIX` environment variable
- ✅ Verifies Tesseract installation during build

### 2. render.yaml
- ✅ Changed from `env: python` to `env: docker`
- ✅ Points to Dockerfile for build

### 3. Health Check Endpoint
- ✅ `/api/health` now reports OCR and Tesseract status
- ✅ Shows Tesseract version if available

### 4. Better Error Logging
- ✅ OCR errors now include environment details
- ✅ Logs PATH and TESSDATA_PREFIX for debugging

## How to Verify the Fix

### Step 1: Check Health Endpoint
After deployment, visit:
```
https://balancebotapi.onrender.com/api/health
```

Look for:
```json
{
  "features": {
    "ocr_available": true,
    "tesseract_available": true,
    "tesseract_version": "5.x.x"
  }
}
```

### Step 2: Run Test Script (Optional)
If you have shell access on Render:
```bash
python test_ocr.py
```

Should show:
```
✅ All OCR tests passed!
```

### Step 3: Test OCR via Frontend
1. Go to https://balancebotai.netlify.app
2. Login
3. Upload a nutrition label image
4. Check if text is extracted

### Step 4: Check Render Logs
Look for these log messages during startup:
```
OCR pipeline imported successfully
NutritionAgent initialized
```

If OCR works, you'll see:
```
OCR extracted XXX characters
```

## Troubleshooting

### If health check shows tesseract_available: false
1. Check Render build logs for "tesseract --version" output
2. Verify Dockerfile is being used (should see Docker build output)
3. Check environment variables in Render dashboard

### If OCR still extracts 0 characters
1. Check the uploaded image quality (must be clear, high resolution)
2. Check Render logs for detailed error messages
3. Try manual entry as fallback

## Files Modified
- `Dockerfile` - New file for Docker deployment
- `.dockerignore` - New file to optimize builds
- `render.yaml` - Updated to use Docker
- `backend/api.py` - Enhanced health check
- `backend/ingest/ocr_reader.py` - Better error logging
- `test_ocr.py` - New test script

## Deployment Steps
1. Push all changes to GitHub
2. Render will auto-deploy (may take 5-10 minutes for Docker build)
3. Check `/api/health` endpoint
4. Test OCR functionality
