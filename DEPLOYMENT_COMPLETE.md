# 🚀 Love Is Complicated - Deployment Complete Guide

## 📦 All Deployment Files Ready

Your challenge is ready to deploy to Render! All necessary files have been created:

### ✅ Deployment Files
- **render.yaml** - Render configuration (auto-detected)
- **requirements_complicated.txt** - Python dependencies (includes gunicorn)
- **app_complicated.py** - Flask app (PORT configured for Render)
- **.gitignore** - Git ignore rules
- **deploy_to_github.bat** - Automated GitHub setup script
- **test_deployment.py** - Deployment verification script
- **DEPLOY_RENDER.md** - Detailed deployment instructions

---

## 🎯 Quick Deploy (3 Steps)

### Step 1: Push to GitHub

**Option A: Use the automated script**
```bash
cd love_is_complicated
deploy_to_github.bat
```
Follow the prompts to enter your GitHub repository URL.

**Option B: Manual commands**
```bash
cd love_is_complicated
git init
git add .
git commit -m "Deploy Love Is Complicated challenge"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/love-is-complicated.git
git push -u origin main
```

### Step 2: Deploy on Render

1. Go to [render.com](https://render.com) and sign in
2. Click **"New +"** → **"Web Service"**
3. Click **"Connect GitHub"** and authorize Render
4. Select your **love-is-complicated** repository
5. Render will auto-detect `render.yaml` ✨
6. Click **"Apply"** to deploy

### Step 3: Test Deployment

```bash
# Test the deployment
python test_deployment.py https://love-is-complicated.onrender.com

# Or test manually
curl https://love-is-complicated.onrender.com
```

---

## 🌐 Your Challenge URL

After deployment (2-3 minutes), your challenge will be live at:

```
https://love-is-complicated.onrender.com
```

Share this URL with CTF participants!

---

## 🔧 Configuration Details

### Render Configuration (render.yaml)
```yaml
services:
  - type: web
    name: love-is-complicated
    env: python
    region: oregon
    plan: free
    branch: main
    buildCommand: pip install -r requirements_complicated.txt
    startCommand: gunicorn app_complicated:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: PORT
        value: 10000
```

### Python Dependencies
```
Flask==3.0.0
pytz==2023.3
requests==2.31.0
gunicorn==21.2.0
```

### Application Configuration
- **Port:** Dynamically set from environment (Render provides PORT)
- **Host:** 0.0.0.0 (accessible from internet)
- **Debug:** False (production mode)

---

## 🧪 Testing Your Deployment

### Test Script
```bash
python test_deployment.py https://love-is-complicated.onrender.com
```

This will test:
- ✅ Homepage loads
- ✅ Proof of Work endpoint
- ✅ Confess endpoint (error handling)
- ✅ robots.txt
- ✅ Time window check

### Manual Testing

**Test homepage:**
```bash
curl https://love-is-complicated.onrender.com
```

**Test PoW endpoint:**
```bash
curl https://love-is-complicated.onrender.com/api/pow
```

**Test confess endpoint:**
```bash
curl -X POST https://love-is-complicated.onrender.com/api/confess
```

**Run full solver (during 2:00-2:30 PM IST):**
```bash
python solution_complicated.py https://love-is-complicated.onrender.com
```

---

## 📊 Monitoring

### View Logs
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click on **love-is-complicated** service
3. Click **"Logs"** tab
4. See real-time logs of all requests

### Check Metrics
- **Events** tab: Deployment history
- **Metrics** tab: CPU, memory usage
- **Settings** tab: Configuration

---

## ⚠️ Important Notes

### Free Tier Behavior
- **Spins down** after 15 minutes of inactivity
- **First request** after spin-down takes 30-60 seconds to wake up
- **750 hours/month** free (sufficient for CTF events)

### For 24/7 Availability
If you need the challenge always available:

**Option 1: Upgrade to paid plan**
- Cost: $7/month
- Unlimited hours
- No spin-down

**Option 2: Keep-alive ping**
Set up a cron job to ping every 10 minutes:
```bash
*/10 * * * * curl https://love-is-complicated.onrender.com
```

### Rate Limiting
The app has built-in exponential backoff rate limiting:
- 1st attempt: 0 seconds
- 2nd attempt: 2 seconds
- 3rd attempt: 4 seconds
- 4th attempt: 8 seconds
- etc.

This prevents brute force attacks and works across all instances.

---

## 🔄 Updating the Challenge

### Automatic Deployment
Render automatically redeploys when you push to GitHub:

```bash
# Make changes to files
git add .
git commit -m "Update challenge"
git push
```

Render will detect the push and redeploy automatically!

### Manual Deployment
1. Go to Render Dashboard
2. Click on your service
3. Click **"Manual Deploy"** → **"Deploy latest commit"**

---

## 🐛 Troubleshooting

### Build Failed
**Check:**
- All dependencies in `requirements_complicated.txt`
- Python version compatibility
- Render build logs for specific errors

**Solution:**
```bash
# Test locally first
pip install -r requirements_complicated.txt
python app_complicated.py
```

### App Not Starting
**Check:**
- `gunicorn app_complicated:app` command is correct
- PORT environment variable is set
- Application logs for errors

**Solution:**
Review logs in Render dashboard for specific error messages.

### 502 Bad Gateway
**Causes:**
- App is still starting (wait 30-60 seconds)
- App crashed (check logs)
- Free tier spinning up from sleep

**Solution:**
Wait a minute and try again. Check logs if persists.

### Rate Limited
**Cause:**
Too many requests from same IP

**Solution:**
Wait for exponential backoff period to expire (shown in error message).

---

## 💰 Cost Breakdown

### Free Tier (Recommended for CTF)
- **Cost:** $0/month
- **Hours:** 750/month
- **Bandwidth:** 100 GB/month
- **Perfect for:** CTF events, testing, demos

### Starter Tier (For 24/7)
- **Cost:** $7/month
- **Hours:** Unlimited
- **Bandwidth:** 100 GB/month
- **Perfect for:** Always-on challenges

---

## 🎯 CTF Deployment Checklist

### Pre-Deployment
- [x] All files created
- [x] render.yaml configured
- [x] requirements.txt includes gunicorn
- [x] app.py uses PORT from environment
- [x] .gitignore configured

### Deployment
- [ ] Push code to GitHub
- [ ] Connect GitHub to Render
- [ ] Verify render.yaml detected
- [ ] Click "Apply" to deploy
- [ ] Wait for build (2-3 minutes)

### Post-Deployment
- [ ] Test homepage loads
- [ ] Test /api/pow endpoint
- [ ] Test /api/confess endpoint
- [ ] Run test_deployment.py
- [ ] Run full solver during valid time
- [ ] Verify flag is returned correctly
- [ ] Share URL with participants
- [ ] Monitor logs during CTF

---

## 📞 Support Resources

### Render Documentation
- [Render Docs](https://render.com/docs)
- [Python on Render](https://render.com/docs/deploy-flask)
- [render.yaml Reference](https://render.com/docs/yaml-spec)

### Challenge Documentation
- **CHALLENGE_COMPLICATED.md** - Full challenge details
- **QUICK_REFERENCE_COMPLICATED.md** - Quick reference
- **DEPLOY_RENDER.md** - Detailed deployment guide
- **README.md** - Overview

### Community
- [Render Community](https://community.render.com)
- [Render Status](https://status.render.com)

---

## 🎉 Success Indicators

Your deployment is successful when:

✅ Homepage loads with "Love Is Complicated" title  
✅ /api/pow returns JSON with timestamp and difficulty  
✅ /api/confess returns error with decoy flag  
✅ robots.txt contains decoy flag  
✅ test_deployment.py passes all tests  
✅ Solver can connect during valid time window  
✅ Real flag is returned when all constraints met  

---

## 🏆 Challenge Statistics

Once deployed, participants will face:

- **Difficulty:** NIGHTMARE
- **Points:** 1500
- **8 salts** with dynamic rotation
- **8 headers** required
- **6-layer HMAC** cryptography
- **Proof of work** (5 leading zeros)
- **TOTP** authentication
- **Browser fingerprinting**
- **24 layers** of obfuscation
- **30+ decoy flags**
- **Expected solve time:** 12-20 hours
- **Expected solve rate:** <1%

---

## 🎊 You're Ready!

Your "Love Is Complicated" challenge is fully configured and ready to deploy!

**Next step:** Run `deploy_to_github.bat` or follow the manual steps above.

**Deployment time:** ~3 minutes  
**Your URL:** `https://love-is-complicated.onrender.com`

Good luck to all participants! They'll need it. 😈💔

---

**Author:** MD  
**Challenge:** Love Is Complicated  
**Version:** 1.0  
**Status:** Ready to Deploy 🚀
