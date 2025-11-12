# Quick Deploy to Railway

This is the **fastest way** to deploy your Web3 Education Platform.

## Prerequisites
- GitHub account
- Railway account (https://railway.app - free sign up)
- Your code pushed to GitHub

## Step-by-Step (5 minutes)

### 1. Push to GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 2. Deploy Backend + Database on Railway

1. Go to https://railway.app
2. Click **"Start a New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository
5. Railway detects Python → Click **"Add variables"**

**Copy/paste these environment variables:**
```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
SECRET_KEY=change-this-to-a-long-random-string-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
GEMINI_API_KEY=your-gemini-api-key
DEBUG=False
PORT=8001
WEB3_RPC_URL=https://rpc.sepolia.org/
WEB3_CHAIN_ID=11155111
STAKING_CONTRACT_ADDRESS=0x76342058da66b1ba50ff62bce2e4934dd03b5d32
ATTESTATION_PRIVATE_KEY=0x05f27cf3b46160eaf3e3a1876e84c451203e83cd0c045ccfa424a8df8cd9ba9c
SCHOLARSHIP_POOL_ADDRESS=your-scholarship-pool-address
THIRDWEB_CLIENT_ID=your-thirdweb-client-id
THIRDWEB_SECRET_KEY=your-thirdweb-secret-key
```

6. Click **Settings** → **Root Directory** → Set to: `server`
7. Click **"+ New"** → **"Database"** → **"Add PostgreSQL"**
8. Click **"Deploy"**
9. Wait 2-3 minutes
10. Copy your backend URL (looks like: `https://web3-edu-platform-production.up.railway.app`)

### 3. Seed Database

After backend deploys:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# Seed database
railway run --service=web3-edu-platform python -m database.seed_reading_data
railway run --service=web3-edu-platform python -m database.seed_writing_data
railway run --service=web3-edu-platform python -m database.seed_quest_data
```

### 4. Deploy Frontend on Vercel

1. Go to https://vercel.com
2. Click **"Add New Project"**
3. Import from GitHub
4. Select your repository
5. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `client`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

6. **Add Environment Variables:**
```env
VITE_API_URL=https://your-backend.railway.app/api
VITE_THIRDWEB_CLIENT_ID=your-thirdweb-client-id
VITE_CHAIN_ID=11155111
VITE_CHAIN_NAME=Sepolia
VITE_STAKING_CONTRACT_ADDRESS=0x76342058da66b1ba50ff62bce2e4934dd03b5d32
```

7. Click **"Deploy"**
8. Wait 1-2 minutes
9. Copy your frontend URL (looks like: `https://web3-edu-platform.vercel.app`)

### 5. Update CORS

Go back to Railway:
1. Open your backend service
2. Click **"Variables"**
3. Add `FRONTEND_URL` = your Vercel URL
4. Redeploy

Or manually update `server/main.py`:
```python
allow_origins=[
    "http://localhost:3000",
    "https://your-app.vercel.app",  # Add your Vercel URL
]
```

### 6. Test!

Visit your Vercel URL and test:
- ✅ Login/Register
- ✅ Connect Wallet
- ✅ Reading practice
- ✅ Writing practice
- ✅ Create commitment (with Sepolia ETH)

## Done! 🎉

Your app is now live:
- **Frontend**: https://your-app.vercel.app
- **Backend**: https://your-backend.railway.app
- **API Docs**: https://your-backend.railway.app/docs

## Costs
- Railway: $5/month (Hobby plan) or free with limitations
- Vercel: Free for personal projects
- Total: ~$0-5/month

## Troubleshooting

**Backend won't start:**
```bash
railway logs --service=your-backend-service
```

**Frontend can't reach backend:**
- Check `VITE_API_URL` has `/api` at the end
- Check CORS settings
- Check backend is running

**Database connection failed:**
- Make sure PostgreSQL is added and linked
- Check `DATABASE_URL` variable exists

Need help? Check the full [DEPLOYMENT_PLAN.md](./DEPLOYMENT_PLAN.md)
