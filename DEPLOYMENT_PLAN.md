# Web3 Education Platform - Deployment Guide

## 🎯 Deployment Options

### Option 1: Railway (Recommended - Easiest)
**Best for:** Full-stack deployment with database in one place
**Cost:** Free tier available, ~$5-10/month for production
**Includes:** Backend, Frontend, PostgreSQL database

### Option 2: Vercel + Railway/Render
**Best for:** Better frontend performance
**Cost:** Free frontend, ~$5/month backend+DB

### Option 3: Self-Hosted (VPS)
**Best for:** Full control, learning DevOps
**Cost:** ~$5-20/month (DigitalOcean, Hetzner)

---

## 🚀 Option 1: Railway Deployment (Recommended)

Railway can deploy everything in one platform with automatic HTTPS, databases, and easy configuration.

### Prerequisites
- GitHub account
- Railway account (sign up at https://railway.app)
- Your code in a GitHub repository

### Step 1: Prepare Your Code

#### A. Add Railway Configuration Files

**1. Create `railway.toml` in project root:**
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "echo 'Use service-specific start commands'"
```

**2. Create `Procfile` in `server/` directory:**
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**3. Create `nixpacks.toml` in `server/` directory:**
```toml
[phases.setup]
nixPkgs = ["python310", "postgresql"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[phases.build]
cmds = ["echo 'No build needed'"]

[start]
cmd = "uvicorn main:app --host 0.0.0.0 --port $PORT"
```

**4. Update `server/requirements.txt` - add gunicorn:**
```txt
# Add this line
gunicorn==21.2.0
```

#### B. Update Frontend Build for Production

**1. Create `client/vercel.json`:**
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

**2. Update `client/vite.config.js`:**
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          web3: ['@thirdweb-dev/react', 'ethers']
        }
      }
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8001',
        changeOrigin: true
      }
    }
  }
})
```

#### C. Push to GitHub

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Prepare for Railway deployment"

# Create GitHub repo and push
git remote add origin https://github.com/yourusername/web3-edu-platform.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Railway

#### A. Deploy Backend + Database

1. **Go to Railway** → https://railway.app
2. **Click "Start a New Project"**
3. **Select "Deploy from GitHub repo"**
4. **Authorize Railway** to access your GitHub
5. **Select your repository**
6. **Configure Backend Service:**
   - Railway will auto-detect the Python app
   - Set **Root Directory**: `server`
   - Click **"Add Variables"** and add:

   ```bash
   # Database (Railway will provide these automatically if you add PostgreSQL)
   DATABASE_URL=${DATABASE_URL}

   # JWT
   SECRET_KEY=your-secret-key-change-in-production-make-it-long-and-random
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=10080

   # AI
   GEMINI_API_KEY=your-gemini-api-key-here

   # Server
   DEBUG=False
   PORT=8001

   # Web3 - Sepolia
   WEB3_RPC_URL=https://rpc.sepolia.org/
   WEB3_CHAIN_ID=11155111
   STAKING_CONTRACT_ADDRESS=0x76342058da66b1ba50ff62bce2e4934dd03b5d32
   ATTESTATION_PRIVATE_KEY=0x05f27cf3b46160eaf3e3a1876e84c451203e83cd0c045ccfa424a8df8cd9ba9c
   SCHOLARSHIP_POOL_ADDRESS=your-scholarship-pool-address

   # Thirdweb
   THIRDWEB_CLIENT_ID=your-thirdweb-client-id
   THIRDWEB_SECRET_KEY=your-thirdweb-secret-key
   ```

7. **Add PostgreSQL Database:**
   - Click **"+ New"** → **"Database"** → **"Add PostgreSQL"**
   - Railway will automatically create `DATABASE_URL` variable
   - Link it to your backend service

8. **Deploy!**
   - Click **"Deploy"**
   - Wait for deployment (2-5 minutes)
   - Railway will give you a URL like: `https://your-app.railway.app`

#### B. Run Database Migrations

After backend is deployed, you need to seed the database:

1. **Go to your backend service** in Railway
2. **Click "Settings"** → **"Service Tokens"** → Create token
3. **Use Railway CLI** locally:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Connect to service
railway run --service=backend bash

# Run migrations
python -m database.seed_reading_data
python -m database.seed_writing_data
python -m database.seed_quest_data
```

**OR** add a migration script to `server/migrate.sh`:
```bash
#!/bin/bash
python -m database.seed_reading_data
python -m database.seed_writing_data
python -m database.seed_quest_data
```

Then run it once after deployment using Railway CLI.

#### C. Deploy Frontend

**Option C1: Deploy Frontend on Railway (same platform)**

1. **In your Railway project** → Click **"+ New"** → **"GitHub Repo"**
2. **Select same repository**
3. **Configure Frontend Service:**
   - Set **Root Directory**: `client`
   - Set **Build Command**: `npm install && npm run build`
   - Set **Start Command**: `npm run preview`
   - Set **Environment Variables**:

   ```bash
   VITE_API_URL=https://your-backend.railway.app/api
   VITE_THIRDWEB_CLIENT_ID=your-thirdweb-client-id
   VITE_CHAIN_ID=11155111
   VITE_CHAIN_NAME=Sepolia
   VITE_STAKING_CONTRACT_ADDRESS=0x76342058da66b1ba50ff62bce2e4934dd03b5d32
   ```

4. **Deploy**
5. **Get your frontend URL**: `https://your-frontend.railway.app`

**Option C2: Deploy Frontend on Vercel (faster, better for React)**

1. **Go to Vercel** → https://vercel.com
2. **Import your GitHub repository**
3. **Configure:**
   - **Framework Preset**: Vite
   - **Root Directory**: `client`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Environment Variables**: (same as above)

4. **Deploy** → Get URL like `https://your-app.vercel.app`

### Step 3: Update CORS Settings

Update `server/main.py` to allow your frontend domain:

```python
# Add your Railway/Vercel frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-frontend.railway.app",
        "https://your-app.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 4: Test Everything

1. **Visit your frontend URL**
2. **Login/Register**
3. **Connect wallet** (make sure it works)
4. **Test reading/writing features**
5. **Test staking** (create a commitment)

---

## 🚀 Option 2: Vercel (Frontend) + Render (Backend)

### Deploy Backend on Render

1. **Go to Render** → https://render.com
2. **Click "New +"** → **"Web Service"**
3. **Connect GitHub repository**
4. **Configure:**
   - **Name**: web3-edu-backend
   - **Root Directory**: `server`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Add Environment Variables** (same as Railway above)

5. **Add PostgreSQL Database:**
   - Click **"New +"** → **"PostgreSQL"**
   - Free tier available
   - Copy the **Internal Database URL**
   - Add as `DATABASE_URL` in web service

6. **Deploy**

### Deploy Frontend on Vercel

(Same as Option 1, Step 2C, Option C2)

---

## 🚀 Option 3: Self-Hosted VPS

### Prerequisites
- VPS (DigitalOcean, Linode, Hetzner, etc.)
- Ubuntu 22.04 LTS
- Domain name (optional but recommended)

### Step 1: Setup Server

```bash
# SSH into your VPS
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3.10 python3.10-venv python3-pip nginx postgresql postgresql-contrib nodejs npm git

# Install Node 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# Install pm2 for process management
npm install -g pm2
```

### Step 2: Setup PostgreSQL

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE web3_edu_platform;
CREATE USER web3user WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE web3_edu_platform TO web3user;
\q
```

### Step 3: Clone and Setup Backend

```bash
# Create app directory
mkdir -p /var/www/web3-edu-platform
cd /var/www/web3-edu-platform

# Clone repo
git clone https://github.com/yourusername/web3-edu-platform.git .

# Setup backend
cd server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file
nano .env
# (Paste your production environment variables)

# Run migrations
python -m database.seed_reading_data
python -m database.seed_writing_data
python -m database.seed_quest_data

# Start with PM2
pm2 start "uvicorn main:app --host 0.0.0.0 --port 8001" --name web3-edu-backend
pm2 save
pm2 startup
```

### Step 4: Setup Frontend

```bash
cd /var/www/web3-edu-platform/client

# Create .env
nano .env
# (Paste your environment variables)

# Build
npm install
npm run build

# Serve with nginx (see nginx config below)
```

### Step 5: Configure Nginx

```bash
nano /etc/nginx/sites-available/web3-edu-platform
```

```nginx
# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

# Frontend
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    root /var/www/web3-edu-platform/client/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8001/api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# Enable site
ln -s /etc/nginx/sites-available/web3-edu-platform /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# Install SSL with Let's Encrypt (optional but recommended)
apt install -y certbot python3-certbot-nginx
certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com
```

---

## 📋 Post-Deployment Checklist

### Backend
- [ ] Backend is running and accessible
- [ ] Database is connected and seeded
- [ ] Environment variables are set correctly
- [ ] API endpoints work (test with `/docs`)
- [ ] CORS is configured for frontend domain

### Frontend
- [ ] Frontend is built and deployed
- [ ] Can access the login page
- [ ] API calls work (check Network tab in browser)
- [ ] Wallet connection works
- [ ] Staking page loads without errors

### Smart Contracts
- [ ] Contract is deployed on Sepolia
- [ ] Contract address is in environment variables
- [ ] Contract is unpaused (if applicable)
- [ ] Test transactions work

### Security
- [ ] Changed all default passwords and keys
- [ ] ATTESTATION_PRIVATE_KEY is secure and not in git
- [ ] SECRET_KEY is random and secure
- [ ] HTTPS is enabled (for production)
- [ ] Database is not publicly accessible

---

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check logs
railway logs --service backend  # Railway
pm2 logs web3-edu-backend      # VPS

# Common issues:
# - Missing environment variables
# - Database connection failed
# - Port already in use
```

### Frontend can't connect to backend
- Check `VITE_API_URL` is correct
- Check CORS settings in `main.py`
- Check browser console for errors
- Try API directly: `https://your-backend.railway.app/docs`

### Database migration fails
```bash
# Check database connection
psql $DATABASE_URL

# Check if tables exist
\dt

# Re-run migrations manually
python -m database.seed_reading_data
```

### Wallet connection issues
- Check `VITE_STAKING_CONTRACT_ADDRESS` is set
- Check `VITE_CHAIN_ID` is 11155111 (Sepolia)
- Check `VITE_THIRDWEB_CLIENT_ID` is valid
- Clear browser cache and reconnect wallet

---

## 💰 Cost Estimate

### Railway (Recommended)
- **Hobby Plan**: $5/month
- **Pro Plan**: $20/month (includes more resources)
- **Database**: Included
- **Total**: ~$5-20/month

### Vercel + Render
- **Vercel Frontend**: Free
- **Render Backend**: $7/month (Starter)
- **Render Database**: Free tier available
- **Total**: ~$0-7/month

### VPS (Self-Hosted)
- **DigitalOcean Droplet**: $6/month (basic)
- **Hetzner VPS**: $4.5/month (better value)
- **Domain**: $10-15/year
- **Total**: ~$5-10/month

---

## 🎯 Recommended Deployment Path

**For Hackathon/Demo:**
→ **Railway** (fastest, all-in-one)

**For Production:**
→ **Vercel (Frontend) + Railway (Backend+DB)** (best performance)

**For Learning/Full Control:**
→ **VPS** (DigitalOcean, Hetzner)

---

## 📞 Support Links

- **Railway**: https://docs.railway.app
- **Vercel**: https://vercel.com/docs
- **Render**: https://render.com/docs
- **Nginx**: https://nginx.org/en/docs/
- **Let's Encrypt**: https://letsencrypt.org/getting-started/

---

**Ready to deploy?** Start with Railway for the easiest path to production! 🚀
