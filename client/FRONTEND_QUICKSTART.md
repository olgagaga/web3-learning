# Frontend Quick Start Guide

## 🚀 Getting Started with Web3 Integration

This guide will help you quickly integrate the Web3 staking feature into your React frontend.

---

## Step 1: Wrap App with ThirdwebProvider

Update `client/src/main.jsx`:

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ThirdwebProvider } from '@thirdweb-dev/react'
import App from './App'
import './styles/index.css'

// Polygon Amoy Testnet Configuration
const activeChain = {
  chainId: parseInt(import.meta.env.VITE_CHAIN_ID || "80002"),
  name: import.meta.env.VITE_CHAIN_NAME || "Polygon Amoy",
  rpc: ['https://rpc-amoy.polygon.technology/'],
  nativeCurrency: {
    name: 'MATIC',
    symbol: 'MATIC',
    decimals: 18,
  },
  blockExplorers: [{
    name: 'PolygonScan',
    url: 'https://amoy.polygonscan.com',
  }],
  testnet: true,
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ThirdwebProvider
      clientId={import.meta.env.VITE_THIRDWEB_CLIENT_ID}
      activeChain={activeChain}
      supportedWallets={[
        'metamask',
        'walletConnect',
        'embeddedWallet',  // Custodial wallet
      ]}
    >
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </ThirdwebProvider>
  </React.StrictMode>
)
```

---

## Step 2: Create Staking API Service

Create `client/src/services/stakingAPI.js`:

```javascript
import api from './api'

const stakingAPI = {
  // Wallet
  connectWallet: (data) => api.post('/staking/wallet/connect', data),
  getWallet: () => api.get('/staking/wallet'),

  // Commitments
  createCommitment: (data) => api.post('/staking/commitments', data),
  getMyCommitments: (status) => api.get('/staking/commitments', {
    params: status ? { status_filter: status } : {}
  }),
  getCommitment: (id) => api.get(`/staking/commitments/${id}`),
  checkProgress: (id) => api.get(`/staking/commitments/${id}/progress`),
  generateAttestation: (id) => api.post(`/staking/commitments/${id}/attest`),
  claimReward: (id, txHash) => api.post(`/staking/commitments/${id}/claim`, {
    commitment_id: id,
    transaction_hash: txHash
  }),
  getCommitmentSummary: (id) => api.get(`/staking/commitments/${id}/summary`),

  // Pods
  createPod: (data) => api.post('/staking/pods', data),
  getOpenPods: () => api.get('/staking/pods'),
  getPod: (id) => api.get(`/staking/pods/${id}`),
  joinPod: (podId, txHash) => api.post(`/staking/pods/${podId}/join`, {
    pod_id: podId,
    transaction_hash: txHash
  }),
  startPod: (id) => api.post(`/staking/pods/${id}/start`),

  // Dashboard
  getDashboard: () => api.get('/staking/dashboard'),
  getTransactions: (limit = 50) => api.get('/staking/transactions', {
    params: { limit }
  }),
  getScholarshipPool: () => api.get('/staking/scholarship-pool'),
}

export default stakingAPI
```

---

## Step 3: Create Web3 Store

Create `client/src/stores/web3Store.js`:

```javascript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

const useWeb3Store = create(
  persist(
    (set, get) => ({
      // State
      wallet: null,
      connected: false,
      balance: '0',
      commitments: [],
      selectedCommitment: null,

      // Actions
      setWallet: (wallet) => set({
        wallet,
        connected: !!wallet
      }),

      setBalance: (balance) => set({ balance }),

      setCommitments: (commitments) => set({ commitments }),

      addCommitment: (commitment) => set((state) => ({
        commitments: [...state.commitments, commitment]
      })),

      updateCommitment: (id, updates) => set((state) => ({
        commitments: state.commitments.map(c =>
          c.id === id ? { ...c, ...updates } : c
        )
      })),

      setSelectedCommitment: (commitment) => set({
        selectedCommitment: commitment
      }),

      disconnect: () => set({
        wallet: null,
        connected: false,
        balance: '0',
        commitments: [],
        selectedCommitment: null,
      }),

      // Selectors
      getActiveCommitments: () => {
        const { commitments } = get()
        return commitments.filter(c => c.status === 'active')
      },

      getCompletedCommitments: () => {
        const { commitments } = get()
        return commitments.filter(c =>
          c.status === 'completed' || c.status === 'claimed'
        )
      },
    }),
    {
      name: 'web3-storage',
      partialize: (state) => ({
        wallet: state.wallet,
        connected: state.connected,
      }),
    }
  )
)

export default useWeb3Store
```

---

## Step 4: Create Wallet Connection Component

Create `client/src/components/wallet/WalletConnect.jsx`:

```jsx
import React, { useEffect, useState } from 'react'
import {
  useAddress,
  useWallet,
  useDisconnect,
  useBalance,
  ConnectWallet
} from '@thirdweb-dev/react'
import useWeb3Store from '../../stores/web3Store'
import stakingAPI from '../../services/stakingAPI'

const WalletConnect = () => {
  const address = useAddress()
  const wallet = useWallet()
  const disconnect = useDisconnect()
  const { data: balance } = useBalance()

  const [syncing, setSyncing] = useState(false)
  const { connected, setWallet, setBalance, disconnect: storeDisconnect } = useWeb3Store()

  // Sync wallet with backend when connected
  useEffect(() => {
    if (address && wallet && !syncing) {
      syncWalletWithBackend()
    }
  }, [address, wallet])

  // Update balance
  useEffect(() => {
    if (balance) {
      setBalance(balance.displayValue)
    }
  }, [balance])

  const syncWalletWithBackend = async () => {
    setSyncing(true)
    try {
      await stakingAPI.connectWallet({
        wallet_address: address,
        wallet_provider: wallet.walletId || 'embedded',
      })

      setWallet({
        address,
        provider: wallet.walletId
      })

      console.log('✓ Wallet synced with backend')
    } catch (error) {
      console.error('Failed to sync wallet:', error)
    } finally {
      setSyncing(false)
    }
  }

  const handleDisconnect = async () => {
    await disconnect()
    storeDisconnect()
  }

  if (!connected || !address) {
    return (
      <div className="wallet-connect-container">
        <ConnectWallet
          theme="light"
          btnTitle="Connect Wallet"
          modalTitle="Choose Wallet"
        />
      </div>
    )
  }

  return (
    <div className="wallet-info flex items-center gap-4 p-2 bg-gray-100 rounded-lg">
      <div className="flex flex-col">
        <span className="text-xs text-gray-500">Wallet</span>
        <span className="font-mono text-sm">
          {address.slice(0, 6)}...{address.slice(-4)}
        </span>
      </div>

      <div className="flex flex-col">
        <span className="text-xs text-gray-500">Balance</span>
        <span className="font-semibold text-sm">
          {parseFloat(balance?.displayValue || '0').toFixed(4)} MATIC
        </span>
      </div>

      <button
        onClick={handleDisconnect}
        className="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600 transition"
      >
        Disconnect
      </button>
    </div>
  )
}

export default WalletConnect
```

---

## Step 5: Add to Header/Navigation

Update your existing header component (e.g., `client/src/components/layout/Header.jsx`):

```jsx
import React from 'react'
import { Link } from 'react-router-dom'
import WalletConnect from '../wallet/WalletConnect'
import useAuthStore from '../../stores/authStore'

const Header = () => {
  const { isAuthenticated } = useAuthStore()

  return (
    <header className="bg-white shadow">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <Link to="/" className="text-2xl font-bold text-orange-500">
          Web3 Education Platform
        </Link>

        <nav className="flex items-center gap-6">
          <Link to="/dashboard" className="hover:text-orange-500">
            Dashboard
          </Link>
          <Link to="/reading" className="hover:text-orange-500">
            Reading
          </Link>
          <Link to="/writing" className="hover:text-orange-500">
            Writing
          </Link>
          <Link to="/staking" className="hover:text-orange-500">
            Staking
          </Link>
          <Link to="/pods" className="hover:text-orange-500">
            Pods
          </Link>

          {isAuthenticated && <WalletConnect />}
        </nav>
      </div>
    </header>
  )
}

export default Header
```

---

## Step 6: Create Staking Page

Create `client/src/pages/StakingPage.jsx`:

```jsx
import React, { useState, useEffect } from 'react'
import { useAddress } from '@thirdweb-dev/react'
import useWeb3Store from '../stores/web3Store'
import stakingAPI from '../services/stakingAPI'
import WalletConnect from '../components/wallet/WalletConnect'
import CreateCommitmentModal from '../components/staking/CreateCommitmentModal'
import CommitmentCard from '../components/staking/CommitmentCard'

const StakingPage = () => {
  const address = useAddress()
  const { connected, commitments, setCommitments } = useWeb3Store()

  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [dashboard, setDashboard] = useState(null)

  useEffect(() => {
    if (connected) {
      loadData()
    }
  }, [connected])

  const loadData = async () => {
    setLoading(true)
    try {
      const [commitmentsRes, dashboardRes] = await Promise.all([
        stakingAPI.getMyCommitments(),
        stakingAPI.getDashboard(),
      ])

      setCommitments(commitmentsRes.data)
      setDashboard(dashboardRes.data)
    } catch (error) {
      console.error('Failed to load staking data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (!connected || !address) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-md mx-auto text-center">
          <h1 className="text-3xl font-bold mb-4">Commitment Staking</h1>
          <p className="text-gray-600 mb-6">
            Connect your wallet to start staking on your learning commitments
          </p>
          <WalletConnect />
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">Loading...</div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Commitment Staking</h1>
        <p className="text-gray-600">
          Stake tokens to commit to your learning goals. Earn rewards for success!
        </p>
      </div>

      {/* Dashboard Stats */}
      {dashboard && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-gray-500 text-sm">Active Commitments</div>
            <div className="text-2xl font-bold text-orange-500">
              {dashboard.active_commitments}
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-gray-500 text-sm">Success Rate</div>
            <div className="text-2xl font-bold text-green-500">
              {dashboard.success_rate.toFixed(0)}%
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-gray-500 text-sm">Total Staked</div>
            <div className="text-2xl font-bold">
              {parseFloat(dashboard.total_staked).toFixed(2)} MATIC
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-gray-500 text-sm">Rewards Earned</div>
            <div className="text-2xl font-bold text-blue-500">
              {parseFloat(dashboard.total_rewards_earned).toFixed(2)} MATIC
            </div>
          </div>
        </div>
      )}

      {/* Create Button */}
      <div className="mb-6">
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-orange-500 text-white px-6 py-3 rounded-lg hover:bg-orange-600 transition"
        >
          + Create New Commitment
        </button>
      </div>

      {/* Commitments List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {commitments.length === 0 ? (
          <div className="col-span-full text-center text-gray-500 py-12">
            No commitments yet. Create your first commitment to get started!
          </div>
        ) : (
          commitments.map((commitment) => (
            <CommitmentCard
              key={commitment.id}
              commitment={commitment}
              onUpdate={loadData}
            />
          ))
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <CreateCommitmentModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false)
            loadData()
          }}
        />
      )}
    </div>
  )
}

export default StakingPage
```

---

## Step 7: Update App Routes

Update `client/src/App.jsx` to add staking routes:

```jsx
import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import MainLayout from './components/layout/MainLayout'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import ReadingPage from './pages/ReadingPage'
import WritingPage from './pages/WritingPage'
import QuestsPage from './pages/QuestsPage'
import BadgesPage from './pages/BadgesPage'
import SettingsPage from './pages/SettingsPage'
import StakingPage from './pages/StakingPage'  // NEW
import PodsPage from './pages/PodsPage'        // NEW
import useAuthStore from './stores/authStore'

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route
        path="/"
        element={
          isAuthenticated ? (
            <MainLayout />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="reading" element={<ReadingPage />} />
        <Route path="writing" element={<WritingPage />} />
        <Route path="quests" element={<QuestsPage />} />
        <Route path="badges" element={<BadgesPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="staking" element={<StakingPage />} />  {/* NEW */}
        <Route path="pods" element={<PodsPage />} />        {/* NEW */}
      </Route>
    </Routes>
  )
}

export default App
```

---

## 📝 Additional Components to Build

You'll also want to create these components (see DEPLOYMENT_GUIDE.md for detailed examples):

1. **CreateCommitmentModal** - Modal for creating new commitments
2. **CommitmentCard** - Display individual commitment with progress
3. **PodsPage** - Browse and join accountability pods
4. **PodCard** - Display pod information
5. **AttestationButton** - Generate and submit attestations
6. **ClaimRewardButton** - Claim completed commitment rewards

---

## 🎨 Styling Tips

Add these Tailwind classes to your components for a polished look:

```css
/* Commitment cards */
.commitment-card {
  @apply bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition;
}

/* Progress bars */
.progress-bar {
  @apply w-full bg-gray-200 rounded-full h-2 overflow-hidden;
}

.progress-bar-fill {
  @apply h-full bg-gradient-to-r from-orange-500 to-orange-600 transition-all duration-500;
}

/* Status badges */
.status-badge {
  @apply px-3 py-1 rounded-full text-xs font-semibold;
}

.status-active {
  @apply bg-blue-100 text-blue-800;
}

.status-completed {
  @apply bg-green-100 text-green-800;
}

.status-failed {
  @apply bg-red-100 text-red-800;
}
```

---

## 🔥 Quick Test Checklist

After implementation, test these user flows:

1. ✅ Connect wallet
2. ✅ View wallet balance
3. ✅ Create a commitment (0.01 MATIC)
4. ✅ View commitment details
5. ✅ Complete some reading/writing activities
6. ✅ Generate attestation
7. ✅ View progress update
8. ✅ Claim reward (after completion)
9. ✅ View transaction history
10. ✅ Browse and join pods

---

## 🚀 Next Steps

1. Follow this guide to implement the basic wallet connection
2. Build the commitment creation interface
3. Add pods browsing and joining
4. Create the staking dashboard with visualizations
5. Test the complete flow end-to-end

For detailed implementation examples and troubleshooting, refer to:
- **DEPLOYMENT_GUIDE.md** - Complete deployment instructions
- **WEB3_FEATURE_SUMMARY.md** - Feature overview and architecture

Happy coding! 🎉
