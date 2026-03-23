# Deploying Love Is Complicated to Render

## 🚀 Quick Deploy

### Option 1: Deploy from GitHub (Recommended)

1. **Push to GitHub**
   ```bash
   cd love_is_complicated
   git init
   git add .
   git commit -m "Initial commit: Love Is Complicated challenge"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/love-is-complicated.git
   git push -u origin main
   ```

2. **Connect to Render**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml`
   - Click "Apply" to deploy

3. **Done!**
   - Your app will be live at: `https://love-is-complicated.onrender.com`

---

### Option 2: Manual Deploy

1. **Go to Render Dashboard**
   - Visit [dashboard.render.com](https://dashboard.render.com)
   - Click "New +" → "Web Service"

2. **Configure Service**
   ```
   Name: love-is-complicated
   Environment: Python 3
   Region: Oregon (or closest to you)
   Branch: main
   Build Command: pip install -r requirements_complicated.txt
   Start Command: gunicorn app_complicated:app
   Plan: Free
   ```

3. **Environment Variables**
   ```
   PYTHON_VERSION = 3.11.0
   PORT = 10000
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait 2-3 minutes for deployment

---

## 📋 Files Required for Deployment

✅ **render.yaml** - Render configuration  
✅ **requirements_complicated.txt** - Python dependencies (includes gunicorn)  
✅ **app_complicated.py** - Flask application (PORT configured)  
✅ **.gitignore** - Git ignore rules

All files are already created and configured!

---

## 🔧 Deployment Configuration

### render.yaml
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

### Requirements
```
Flask==3.0.0
pytz==2023.3
requests==2.31.0
gunicorn==21.2.0
```

---

## 🌐 After Deployment

### Your Challenge URL
```
https://love-is-complicated.onrender.com
```

### Test the Deployment
```bash
# Check if server is running
curl https://love-is-complicated.onrender.com

# Test with solver (during 2:00-2:30 PM IST)
python solution_complicated.py https://love-is-complicated.onrender.com
```

---

## ⚠️ Important Notes

### Free Tier Limitations
- **Spins down after 15 minutes of inactivity**
- **First request after spin-down takes 30-60 seconds**
- **750 hours/month free** (enough for CTF)

### For CTF Events
If you need 24/7 uptime:
1. Upgrade to paid plan ($7/month)
2. Or use a cron job to ping every 10 minutes:
   ```bash
   */10 * * * * curl https://love-is-complicated.onrender.com
   ```

### Rate Limiting
The app has built-in rate limiting with exponential backoff. This works across all instances.

---

## 🔍 Monitoring

### View Logs
1. Go to Render Dashboard
2. Click on your service
3. Click "Logs" tab
4. See real-time logs

### Check Status
```bash
curl https://love-is-complicated.onrender.com/api/pow
```

Should return:
```json
{
  "timestamp": 1234567890,
  "difficulty": 5,
  "hint": "Find nonce where SHA256(timestamp + nonce) starts with 00000"
}
```

---

## 🐛 Troubleshooting

### Build Failed
- Check `requirements_complicated.txt` has all dependencies
- Verify Python version compatibility
- Check Render logs for specific errors

### App Not Starting
- Verify `gunicorn app_complicated:app` command
- Check PORT environment variable
- Review application logs

### 502 Bad Gateway
- App is starting (wait 30-60 seconds)
- Or app crashed (check logs)

### Rate Limited
- Wait for exponential backoff period
- Check logs for rate limit messages

---

## 🔄 Updating the Challenge

### Push Updates
```bash
git add .
git commit -m "Update challenge"
git push
```

Render will automatically redeploy!

### Manual Redeploy
1. Go to Render Dashboard
2. Click "Manual Deploy" → "Deploy latest commit"

---

## 💰 Cost Estimate

### Free Tier
- **Cost:** $0/month
- **Hours:** 750/month
- **Perfect for:** CTF events, testing

### Starter Tier
- **Cost:** $7/month
- **Hours:** Unlimited
- **Perfect for:** 24/7 availability

---

## 🎯 CTF Deployment Checklist

- [ ] Push code to GitHub
- [ ] Connect GitHub to Render
- [ ] Verify render.yaml is detected
- [ ] Deploy service
- [ ] Wait for build to complete (2-3 minutes)
- [ ] Test homepage loads
- [ ] Test /api/pow endpoint
- [ ] Run solver during valid time window
- [ ] Verify flag is returned
- [ ] Share URL with participants
- [ ] Monitor logs during CTF

---

## 📞 Support

### Render Support
- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com)

### Challenge Issues
- Check CHALLENGE_COMPLICATED.md
- Review QUICK_REFERENCE_COMPLICATED.md
- Verify timing constraints

---

## 🎉 Success!

Once deployed, your challenge will be live at:
```
https://love-is-complicated.onrender.com
```

Share this URL with CTF participants and watch them struggle! 😈💔

---

**Deployment Time:** ~3 minutes  
**Difficulty:** NIGHTMARE  
**Points:** 1500  
**Expected Solve Rate:** <1%

Good luck to all participants! 🏆
