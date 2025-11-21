# Deployment Guide: AI Hedge Fund System

This guide provides step-by-step instructions for deploying the AI Hedge Fund System to production using the **Hybrid Architecture** (Frontend on Vercel + Backend on Railway/Render).

## Table of Contents

- [Prerequisites](#prerequisites)
- [Architecture Overview](#architecture-overview)
- [Option 1: Vercel + Railway (Recommended)](#option-1-vercel--railway-recommended)
- [Option 2: Vercel + Render](#option-2-vercel--render)
- [Post-Deployment Configuration](#post-deployment-configuration)
- [Testing Your Deployment](#testing-your-deployment)
- [Troubleshooting](#troubleshooting)
- [Cost Estimates](#cost-estimates)

---

## Prerequisites

Before deploying, ensure you have:

1. **Git Repository**:
   - Push your code to GitHub/GitLab/Bitbucket
   - Ensure `.env` is in `.gitignore` (already configured)

2. **API Keys** (at least one LLM provider):
   - **Gemini API Key** (recommended, free tier): Get from [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
   - OR **OpenAI API Key**: Get from [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
   - OR **Anthropic API Key**: Get from [https://console.anthropic.com/](https://console.anthropic.com/)
   - Optional: **News API Key**: Get from [https://newsapi.org/](https://newsapi.org/)

3. **Platform Accounts** (free to sign up):
   - [Vercel Account](https://vercel.com/signup) (for frontend)
   - [Railway Account](https://railway.app/) (for backend) OR [Render Account](https://render.com/)

4. **Local Setup** (for testing before deployment):
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt

   # Install frontend dependencies
   cd frontend && npm install
   ```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│              Vercel (Frontend - CDN)                    │
│  • Static React app served globally                     │
│  • Fast loading with edge caching                       │
│  • Automatic HTTPS                                      │
│  URL: https://your-app.vercel.app                       │
└──────────────────────┬──────────────────────────────────┘
                       │
                       │ API Calls (HTTPS)
                       ▼
┌─────────────────────────────────────────────────────────┐
│        Railway/Render (Backend - FastAPI)               │
│  • Python FastAPI server                                │
│  • 4-agent analysis engine                              │
│  • Persistent process with in-memory cache              │
│  URL: https://your-api.railway.app                      │
└─────────────────────────────────────────────────────────┘
```

**Benefits of Hybrid Architecture:**
- ✅ No code changes required
- ✅ Frontend on global CDN (fast worldwide)
- ✅ Backend can run long-lived processes
- ✅ In-memory caching works perfectly
- ✅ File system access for logs
- ✅ Deploy in 1-2 hours
- ✅ Cost-effective ($5-10/month)

---

## Option 1: Vercel + Railway (Recommended)

### Step 1: Deploy Backend to Railway

1. **Create Railway Account**:
   - Go to [railway.app](https://railway.app/)
   - Sign up with GitHub (recommended)

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `ai_hedge_fund_system` repository
   - Railway will auto-detect Python and install dependencies

3. **Configure Environment Variables**:
   - In Railway dashboard, go to your project
   - Click on "Variables" tab
   - Add the following variables:

   ```env
   # Required: LLM Provider
   LLM_PROVIDER=gemini

   # Required: API Key (choose one based on LLM_PROVIDER)
   GEMINI_API_KEY=your_gemini_api_key_here
   # OR
   # OPENAI_API_KEY=your_openai_key_here
   # OR
   # ANTHROPIC_API_KEY=your_anthropic_key_here

   # Optional: Enable adaptive weights
   ENABLE_ADAPTIVE_WEIGHTS=true

   # Optional: News API
   NEWS_API_KEY=your_news_api_key_here

   # Python version (auto-detected)
   PYTHON_VERSION=3.13
   ```

4. **Configure Deployment Settings**:
   - Railway should auto-detect `railway.toml`
   - Start Command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - Health Check Path: `/health`
   - Railway will automatically assign a port

5. **Deploy**:
   - Click "Deploy"
   - Wait 3-5 minutes for build to complete
   - Railway will provide a URL like: `https://your-app.railway.app`

6. **Test Backend**:
   - Visit: `https://your-app.railway.app/docs`
   - You should see the Swagger API documentation
   - Test the `/health` endpoint to ensure all 4 agents are working

### Step 2: Deploy Frontend to Vercel

1. **Update Frontend Environment Configuration**:

   Before deploying, update the API URL configuration:

   ```bash
   # In /frontend directory, create or update .env.production
   echo "VITE_API_URL=https://your-app.railway.app" > .env.production
   ```

2. **Create Vercel Account**:
   - Go to [vercel.com](https://vercel.com/)
   - Sign up with GitHub (recommended)

3. **Import Project**:
   - Click "Add New..." → "Project"
   - Select your `ai_hedge_fund_system` repository
   - Vercel will auto-detect the framework

4. **Configure Build Settings**:
   - Framework Preset: **Vite**
   - Root Directory: `frontend`
   - Build Command: `npm run build` (auto-detected)
   - Output Directory: `dist` (auto-detected)

5. **Configure Environment Variables**:
   - In "Environment Variables" section, add:

   ```env
   VITE_API_URL=https://your-app.railway.app
   ```

   **IMPORTANT**: Replace `https://your-app.railway.app` with your actual Railway URL from Step 1

6. **Deploy**:
   - Click "Deploy"
   - Wait 2-3 minutes for build to complete
   - Vercel will provide a URL like: `https://your-app.vercel.app`

### Step 3: Update Backend CORS Configuration

Now that you have your Vercel URL, update the backend to allow requests from it:

1. **Go to Railway Dashboard**:
   - Open your project
   - Go to "Variables" tab

2. **Add CORS Configuration**:
   ```env
   ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:5173,http://localhost:5174
   ```

   **IMPORTANT**: Replace `https://your-app.vercel.app` with your actual Vercel URL

3. **Redeploy Backend**:
   - Railway will automatically redeploy with new environment variables
   - Wait 1-2 minutes for redeployment

### Step 4: Verify End-to-End

1. **Visit Your Frontend**:
   - Go to `https://your-app.vercel.app`
   - You should see the dashboard loading

2. **Test Stock Analysis**:
   - Go to "Stock Analysis" page
   - Enter a symbol like "AAPL"
   - Click "Analyze"
   - You should see the 4-agent analysis with investment narrative

3. **Check Console** (if issues):
   - Press F12 to open Developer Tools
   - Check Console tab for errors
   - Common issues: CORS errors (check ALLOWED_ORIGINS), API URL mismatch

---

## Option 2: Vercel + Render

If you prefer Render over Railway, follow these steps:

### Step 1: Deploy Backend to Render

1. **Create Render Account**:
   - Go to [render.com](https://render.com/)
   - Sign up with GitHub (recommended)

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select `ai_hedge_fund_system`

3. **Configure Service**:
   - **Name**: `ai-hedge-fund-api`
   - **Region**: Oregon (or closest to your users)
   - **Branch**: `main`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

4. **Choose Plan**:
   - **Free** (for testing) - sleeps after 15 mins of inactivity
   - **Starter** ($7/month) - always on, recommended for production

5. **Add Environment Variables**:
   Click "Advanced" → "Add Environment Variable":

   ```env
   PYTHON_VERSION=3.13
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=your_gemini_api_key_here
   ENABLE_ADAPTIVE_WEIGHTS=true
   ```

6. **Create Web Service**:
   - Click "Create Web Service"
   - Wait 5-10 minutes for initial build
   - Render will provide a URL like: `https://ai-hedge-fund-api.onrender.com`

7. **Configure Health Check**:
   - In service settings, set Health Check Path: `/health`

8. **Test Backend**:
   - Visit: `https://ai-hedge-fund-api.onrender.com/docs`

### Step 2: Deploy Frontend to Vercel

Follow the same steps as in Option 1, Step 2, but use your Render URL instead:

```env
VITE_API_URL=https://ai-hedge-fund-api.onrender.com
```

### Step 3: Update Backend CORS

In Render dashboard, add environment variable:

```env
ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:5173,http://localhost:5174
```

Then manually redeploy from Render dashboard.

---

## Post-Deployment Configuration

### 1. Custom Domain (Optional)

**Vercel (Frontend)**:
- Go to Project Settings → Domains
- Add your custom domain (e.g., `hedge-fund.yourdomain.com`)
- Follow DNS configuration instructions
- Vercel provides automatic HTTPS

**Railway (Backend)**:
- Go to Settings → Networking
- Add custom domain (e.g., `api.yourdomain.com`)
- Follow DNS configuration instructions

**Update CORS**:
After adding custom domains, update `ALLOWED_ORIGINS` to include them.

### 2. Enable Auto-Deploy

**Vercel**:
- Automatically enabled for the `main` branch
- Every push to `main` triggers a deployment
- Pull requests get preview deployments

**Railway**:
- Go to Settings → Deploys
- Enable "Auto Deploy" for `main` branch

**Render**:
- Automatically enabled by default
- Configure in Settings → Build & Deploy

### 3. Monitoring Setup

**Vercel Analytics** (Optional, $10/month):
- Go to Project → Analytics
- Enable Web Analytics
- Get insights on page views, performance

**Railway Metrics**:
- Built-in CPU, memory, and network metrics
- Access via Metrics tab in dashboard

**Render Metrics**:
- Built-in metrics in dashboard
- Set up alerts for downtime

### 4. Backup Strategy

**Environment Variables**:
- Download and save all environment variables securely
- Store in password manager (1Password, LastPass)

**Database** (when added in Phase 2):
- Enable automated backups on Railway/Render
- Configure backup retention (7 days recommended)

---

## Testing Your Deployment

### Automated Testing

1. **Backend Health Check**:
   ```bash
   curl https://your-api.railway.app/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "timestamp": "2024-01-20T12:00:00",
     "agents": {
       "fundamentals": "operational",
       "momentum": "operational",
       "quality": "operational",
       "sentiment": "operational"
     },
     "version": "4.0.0"
   }
   ```

2. **Test Stock Analysis API**:
   ```bash
   curl -X POST "https://your-api.railway.app/analyze" \
        -H "Content-Type: application/json" \
        -d '{"symbol": "AAPL"}'
   ```

3. **Frontend Loading**:
   - Visit `https://your-app.vercel.app`
   - Check that all pages load correctly
   - Test navigation between pages

### Manual Testing Checklist

- [ ] Dashboard loads without errors
- [ ] Stock Analysis page works (analyze AAPL, MSFT, GOOGL)
- [ ] Portfolio page displays correctly
- [ ] Backtesting page loads (may take time to run)
- [ ] Paper Trading page shows virtual portfolio
- [ ] System Details page displays architecture
- [ ] All navigation links work
- [ ] Toast notifications appear for actions
- [ ] Error handling works (try invalid symbol like "INVALID")

---

## Troubleshooting

### Common Issues

#### 1. CORS Errors in Browser Console

**Symptom**: `Access to fetch at 'https://...' from origin 'https://...' has been blocked by CORS policy`

**Solution**:
- Verify `ALLOWED_ORIGINS` includes your Vercel domain
- Ensure no trailing slashes in URLs
- Check that backend redeployed after adding variable
- Test backend health endpoint directly in browser

#### 2. "Failed to fetch" or Network Errors

**Symptom**: Frontend shows "Failed to analyze stock" errors

**Solution**:
- Check that `VITE_API_URL` is set correctly in Vercel
- Verify backend is running (visit `/health` endpoint)
- Check Railway/Render logs for errors
- Ensure backend isn't sleeping (upgrade from free tier on Render)

#### 3. "Agents Not Operational" in Health Check

**Symptom**: `/health` endpoint shows some agents as "failed"

**Solution**:
- Check Railway/Render logs for specific agent errors
- Verify LLM API key is set correctly
- Ensure `LLM_PROVIDER` matches the API key you provided
- Check for yfinance rate limiting (restart service)

#### 4. Build Failures

**Frontend Build Fails**:
- Check that `npm install` succeeds locally
- Verify all dependencies in `package.json` are accessible
- Check Vercel build logs for specific error

**Backend Build Fails**:
- Check that `requirements.txt` is valid
- Verify Python version compatibility (3.9+)
- Check Railway/Render build logs
- Ensure `talib-binary` installs correctly (usually auto-handled)

#### 5. Slow Response Times

**Symptom**: Analysis takes >30 seconds or times out

**Possible Causes**:
- Cold start on free tier (Render sleeps after 15 mins)
- yfinance API rate limiting
- LLM API timeout

**Solutions**:
- Upgrade to paid tier (Railway: $5/mo, Render: $7/mo)
- Reduce concurrent analysis requests
- Check LLM API quota/limits
- Implement request queuing (Phase 2)

#### 6. Environment Variables Not Loading

**Symptom**: Backend errors about missing API keys

**Solution**:
- Verify variables are set in Railway/Render dashboard (not just in .env)
- Check for typos in variable names
- Ensure no quotes around values in dashboard
- Manually trigger redeploy after adding variables

---

## Cost Estimates

### Free Tier (Testing)

| Service | Plan | Cost | Limitations |
|---------|------|------|-------------|
| Vercel | Hobby | **$0/month** | 100GB bandwidth, unlimited projects |
| Railway | Trial | **$5 credit** | $5 lasts ~1 month with minimal traffic |
| Render | Free | **$0/month** | Sleeps after 15 mins, 750 hours/month |
| **Total** | | **~$0-5/month** | Good for testing, not production |

### Recommended Production

| Service | Plan | Cost | Benefits |
|---------|------|------|----------|
| Vercel | Pro | **$20/month** | Team features, analytics, priority support |
| Railway | Starter | **$5-10/month** | Based on usage, always on |
| **OR** Render | Starter | **$7/month** | Always on, 512MB RAM |
| **Total** | | **$12-30/month** | Production-ready, reliable |

### Phase 2+ (With Database & Redis)

| Service | Plan | Cost |
|---------|------|------|
| Vercel (Frontend) | Pro | $20/month |
| Railway (Backend) | Pro | $20/month |
| Supabase (PostgreSQL) | Pro | $25/month |
| Upstash (Redis) | Free | $0/month (10K requests/day) |
| **Total** | | **$65/month** |

**Note**: These are estimates. Railway charges based on actual resource usage.

---

## Next Steps

After successful deployment:

1. **Phase 2: Add Database & Redis** (see CLAUDE.md)
   - Migrate to PostgreSQL for persistent storage
   - Add Redis for distributed caching
   - Improve performance and reliability

2. **Phase 3: Add User Authentication**
   - Implement JWT-based authentication
   - User-specific portfolios
   - Secure API endpoints

3. **Phase 4: Monitoring & Alerts**
   - Set up Sentry for error tracking
   - Add Prometheus metrics
   - Configure uptime monitoring

4. **Phase 5: Advanced Features**
   - Mobile app (React Native)
   - Automated trading integration (Alpaca)
   - Advanced ML features

---

## Support

If you encounter issues not covered in this guide:

1. **Check Logs**:
   - Railway: Dashboard → Logs tab
   - Render: Dashboard → Logs
   - Vercel: Dashboard → Deployments → View Function Logs

2. **Review Documentation**:
   - `CLAUDE.md` - System architecture and development guide
   - `README.md` - Project overview
   - `SECURITY.md` - Security best practices

3. **Common Log Locations**:
   - Backend logs: Check Railway/Render dashboard
   - Frontend console: Press F12 → Console tab
   - API logs: `logs/api/api.log` (not accessible in production, check dashboard)

---

## Security Checklist

Before going to production:

- [ ] All API keys stored as environment variables (not in code)
- [ ] `.env` file in `.gitignore`
- [ ] `ALLOWED_ORIGINS` set to specific domains (not `*`)
- [ ] HTTPS enabled on both frontend and backend (automatic on Vercel/Railway/Render)
- [ ] Health check endpoint accessible for monitoring
- [ ] Secrets not exposed in frontend (all in backend)
- [ ] Rate limiting considered (add in Phase 2)
- [ ] Error messages don't leak sensitive information

---

## Rollback Procedure

If deployment causes issues:

**Vercel**:
1. Go to Deployments
2. Find previous working deployment
3. Click "..." → "Promote to Production"

**Railway**:
1. Go to Deployments tab
2. Click "Rollback" on previous deployment

**Render**:
1. Go to Events tab
2. Find previous successful deploy
3. Click "Redeploy" with previous commit

**Git**:
```bash
# Revert to previous commit
git revert HEAD
git push origin main

# Or rollback to specific commit
git reset --hard <commit-hash>
git push origin main --force
```

---

**Congratulations!** 🎉 Your AI Hedge Fund System is now live in production. Happy trading! 📈
