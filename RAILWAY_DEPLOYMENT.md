# Railway Deployment Guide

## Prerequisites
- Railway account ([railway.app](https://railway.app))
- GitHub repository with your code
- Deployed smart contracts on Sepolia testnet
- Thirdweb account with Client ID
- Gemini API key

## Architecture
This deployment creates 3 Railway services:
1. **PostgreSQL Database** - Managed database service
2. **Backend API** - Python/FastAPI server
3. **Frontend** - Vite/React application

---

## Step 1: Push Your Code to GitHub

```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

---

## Step 2: Create a New Railway Project

1. Go to [railway.app](https://railway.app) and log in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub account
5. Select your `web3-edu-platform` repository

---

## Step 3: Add PostgreSQL Database

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway will provision a PostgreSQL database
4. Note: The `DATABASE_URL` environment variable is automatically created

---

## Step 4: Deploy the Backend Service

1. Click **"+ New"** → **"GitHub Repo"**
2. Select your repository again
3. **IMPORTANT**: Configure the service:
   - **Service Name**: `backend` or `api`
   - **Root Directory**: `server` (without leading slash)
   - Railway will auto-detect Python 3.12 from `.python-version` file

4. Add environment variables (click on the service → **Variables** tab):
   ```
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   SECRET_KEY=<generate-random-secret-key>
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   GEMINI_API_KEY=<your-gemini-api-key>
   DEBUG=False
   PORT=8000
   ALLOWED_ORIGINS=<will-add-after-frontend-deployment>
   WEB3_RPC_URL=https://rpc.sepolia.org/
   WEB3_CHAIN_ID=11155111
   STAKING_CONTRACT_ADDRESS=<your-deployed-contract-address>
   ATTESTATION_PRIVATE_KEY=<your-attestation-private-key>
   SCHOLARSHIP_POOL_ADDRESS=<your-scholarship-pool-address>
   THIRDWEB_CLIENT_ID=<your-thirdweb-client-id>
   THIRDWEB_SECRET_KEY=<your-thirdweb-secret-key>
   ```

   **Note**: `DATABASE_URL` will reference the PostgreSQL service automatically

5. Click **"Deploy"**
6. Once deployed, copy the service URL (e.g., `https://backend-production-xxxx.up.railway.app`)

---

## Step 5: Deploy the Frontend Service

1. Click **"+ New"** → **"GitHub Repo"**
2. Select your repository again
3. **IMPORTANT**: Configure the service:
   - **Service Name**: `frontend` or `client`
   - **Root Directory**: `client` (without leading slash)

4. Add environment variables:
   ```
   VITE_API_URL=<backend-url-from-step-4>/api
   VITE_THIRDWEB_CLIENT_ID=<your-thirdweb-client-id>
   VITE_CHAIN_ID=11155111
   VITE_CHAIN_NAME=Sepolia
   VITE_STAKING_CONTRACT_ADDRESS=<your-staking-contract-address>
   VITE_ESCROW_CONTRACT_ADDRESS=<your-escrow-contract-address>
   VITE_REPUTATION_SBT_ADDRESS=<your-reputation-sbt-address>
   VITE_SCHOLARSHIP_POOL_ADDRESS=<your-scholarship-pool-address>
   ```

5. Click **"Deploy"**
6. Once deployed, copy the frontend URL (e.g., `https://web3-edu-platform-production-xxxx.up.railway.app`)

---

## Step 6: Update Backend CORS Settings

1. Go back to your **backend service**
2. Update the `ALLOWED_ORIGINS` environment variable:
   ```
   ALLOWED_ORIGINS=<frontend-url-from-step-5>,https://your-custom-domain.com
   ```
   Example: `ALLOWED_ORIGINS=https://web3-edu-platform-production-xxxx.up.railway.app`

3. The backend will automatically redeploy with the new CORS settings

---

## Step 7: Verify Deployment

1. Open your frontend URL in a browser
2. Check the browser console for any errors
3. Test the following:
   - User registration and login
   - API connectivity
   - Wallet connection
   - Smart contract interactions

---

## Step 8: (Optional) Add Custom Domain

### For Frontend:
1. Go to your frontend service settings
2. Click **"Settings"** → **"Domains"**
3. Click **"Add Domain"**
4. Enter your custom domain (e.g., `app.yourdomain.com`)
5. Add the CNAME record to your DNS provider:
   - Type: `CNAME`
   - Name: `app` (or your subdomain)
   - Value: `<provided-by-railway>`

### For Backend:
1. Go to your backend service settings
2. Click **"Settings"** → **"Domains"**
3. Click **"Add Domain"**
4. Enter your API subdomain (e.g., `api.yourdomain.com`)
5. Add the CNAME record to your DNS provider

6. Update environment variables:
   - Frontend: Update `VITE_API_URL` to use custom domain
   - Backend: Update `ALLOWED_ORIGINS` to include custom domain

---

## Environment Variables Quick Reference

### Backend Required Variables:
- `DATABASE_URL` (auto-set by Railway)
- `SECRET_KEY` (generate with: `openssl rand -hex 32`)
- `GEMINI_API_KEY`
- `ALLOWED_ORIGINS`
- `STAKING_CONTRACT_ADDRESS`
- `THIRDWEB_CLIENT_ID`
- `THIRDWEB_SECRET_KEY`

### Frontend Required Variables:
- `VITE_API_URL`
- `VITE_THIRDWEB_CLIENT_ID`
- `VITE_STAKING_CONTRACT_ADDRESS`
- `VITE_SCHOLARSHIP_POOL_ADDRESS`

---

## Troubleshooting

### Backend won't start:
1. Check logs in Railway dashboard
2. Verify all required environment variables are set
3. Ensure `DATABASE_URL` is correctly linked
4. Check Python dependencies in `requirements.txt`

### Python version compatibility error (pydantic build failure):
The project uses Python 3.12 via `server/.python-version` file for compatibility with `pydantic==2.5.0`. If you see pydantic-core build errors:

1. **Verify Root Directory is set correctly:**
   - In Railway service settings, ensure Root Directory is `server` (not `/server`)
   - This allows Railway to detect the `.python-version` file

2. **Check the deployment logs:**
   - Look for "Found CPython 3.12" (correct) vs "Found CPython 3.13" (wrong)
   - If it shows 3.13, the `.python-version` file isn't being detected

3. **Alternative: Upgrade pydantic** (if you prefer Python 3.13):
   ```bash
   cd server
   pip install pydantic==2.10.0 pydantic-settings==2.6.1 --upgrade
   pip freeze > requirements.txt
   git add requirements.txt .python-version
   git commit -m "Upgrade pydantic for Python 3.13"
   git push
   ```

### Frontend can't connect to backend:
1. Verify `VITE_API_URL` points to correct backend URL
2. Check backend `ALLOWED_ORIGINS` includes frontend URL
3. Open browser console to see CORS errors

### Database connection errors:
1. Ensure backend is linked to PostgreSQL service
2. Check `DATABASE_URL` format in backend variables
3. Verify network connectivity between services

### Smart contract interactions fail:
1. Verify contract addresses are correct
2. Ensure you're using the right network (Sepolia)
3. Check Thirdweb Client ID is valid
4. Confirm wallet has test ETH

---

## Monitoring and Logs

- View service logs: Click on service → **"Deployments"** → **"View Logs"**
- Monitor metrics: Service dashboard shows CPU, memory, and network usage
- Set up alerts in Railway dashboard for downtime notifications

---

## Cost Optimization

- Railway offers $5 free credit per month
- Estimated monthly cost: ~$10-20 for all services
- Scale down resources during development
- Use Railway's sleep feature for non-production environments

---

## Automatic Deployments

Railway automatically redeploys when you push to your main branch:
```bash
git add .
git commit -m "Update feature"
git push origin main
```

To disable auto-deploy: Service Settings → **"Deploy Triggers"** → Toggle off

---

## Security Checklist

- [ ] Change all default secrets and API keys
- [ ] Set `DEBUG=False` in production
- [ ] Use strong `SECRET_KEY` (32+ random characters)
- [ ] Never commit `.env` files to git
- [ ] Keep `ATTESTATION_PRIVATE_KEY` secure
- [ ] Regularly rotate API keys
- [ ] Enable Railway's built-in DDoS protection
- [ ] Use HTTPS only (Railway provides this automatically)

---

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub Issues: [Your repo issues page]
