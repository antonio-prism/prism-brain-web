# 🎯 PRISM Brain Backend - Simplified Structure

## 📦 ALL FILES IN ROOT DIRECTORY

This package has been simplified - all Python files are in the root directory.

**No more `backend/` folder issues!**

---

## 🚀 INSTALLATION (Copy-Paste These Commands)

```bash
# Navigate to Downloads
cd Downloads

# Extract
tar -xzf prism_brain_live_probabilities_v3_FIXED.tar.gz
cd prism_brain_live_backend_v3

# Initialize Git
git init
git add .
git commit -m "PRISM Brain v3.0 - Simplified structure"
git branch -M main

# Connect to GitHub
git remote add origin https://github.com/antonio-prism/prism-brain-web.git

# Force push
git push -f origin main
```

---

## ⚙️ UPDATE RENDER SETTINGS

**IMPORTANT**: After pushing, update your Render service settings:

1. Go to: https://dashboard.render.com/
2. Click: **prism-brain-backend**
3. Click: **Settings** (left sidebar)
4. Under "Build & Deploy":
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn full_calculator_live:app --host 0.0.0.0 --port $PORT`
5. Click **"Save Changes"**
6. Click **"Manual Deploy"** → **"Clear build cache & deploy"**

---

## ✅ EXPECTED RESULT

After deployment, you should see:

```
==> Installing Python version 3.11.0...
==> pip install -r requirements.txt
==> Successfully installed fastapi uvicorn...
==> Build successful 🎉
==> Running 'uvicorn full_calculator_live:app...'
🚀 PRISM Brain Full Calculator Backend Started
✓ Risk Database: 13 risks loaded
✓ API Version: 3.0.0
==> Live ✅
```

---

## 🧪 TEST

```bash
curl https://prism-brain-backend.onrender.com/api/health
```

Should return:
```json
{
  "status": "healthy",
  "calculator_version": "3.0.0",
  "risks_loaded": 13
}
```

---

## 📁 FILE STRUCTURE (SIMPLIFIED)

```
prism_brain_simple/
├── full_calculator.py ......... Backend code (569 lines)
├── requirements.txt ........... Dependencies
├── runtime.txt ................ Python 3.11.0
├── Procfile ................... Start command
├── .gitignore ................. Git ignore
└── README.md .................. This file
```

**No backend/ folder - everything in root!**

---

## 🎯 KEY POINTS

1. ✅ All files in root directory (no subfolders)
2. ✅ Procfile command: `uvicorn full_calculator_live:app`
3. ✅ Render build command: `pip install -r requirements.txt`
4. ✅ Render start command: `uvicorn full_calculator_live:app --host 0.0.0.0 --port $PORT`
5. ✅ Python version: 3.11.0 (from runtime.txt)

---

## 🔧 RENDER SERVICE SETTINGS

Make sure these are set in Render dashboard:

| Setting | Value |
|---------|-------|
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn full_calculator_live:app --host 0.0.0.0 --port $PORT` |
| **Auto-Deploy** | Yes |
| **Branch** | main |

---

## ✨ THIS WILL WORK!

Simplified structure = no path issues = successful deployment! 🚀


## Manual live update
Trigger a refresh (manual mode):
- POST /api/probabilities/update
Then check:
- GET /api/health
- GET /api/risks/live
- GET /api/signals/recent?hours=24
- GET /docs
