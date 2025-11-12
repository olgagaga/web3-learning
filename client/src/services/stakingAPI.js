import api from './api'

const stakingAPI = {
  // Wallet
  connectWallet: (data) => api.post('/staking/wallet/connect', data),
  getWallet: () => api.get('/staking/wallet'),

  // Commitments
  createCommitment: (data) => api.post('/staking/commitments', data),
  getMyCommitments: (statusFilter) =>
    api.get('/staking/commitments', { params: statusFilter ? { status_filter: statusFilter } : {} }),
  getCommitment: (id) => api.get(`/staking/commitments/${id}`),
  checkProgress: (id) => api.get(`/staking/commitments/${id}/progress`),
  generateAttestation: (id) => api.post(`/staking/commitments/${id}/attest`),
  claimReward: (id, txHash) =>
    api.post(`/staking/commitments/${id}/claim`, {
      commitment_id: id,
      transaction_hash: txHash
    }),
  getCommitmentSummary: (id) => api.get(`/staking/commitments/${id}/summary`),

  // Pods
  createPod: (data) => api.post('/staking/pods', data),
  getOpenPods: () => api.get('/staking/pods'),
  getPod: (id) => api.get(`/staking/pods/${id}`),
  joinPod: (podId, txHash) =>
    api.post(`/staking/pods/${podId}/join`, {
      pod_id: podId,
      transaction_hash: txHash
    }),
  startPod: (id) => api.post(`/staking/pods/${id}/start`),

  // Dashboard
  getDashboard: () => api.get('/staking/dashboard'),
  getTransactions: (limit = 50) =>
    api.get('/staking/transactions', { params: { limit } }),
  getScholarshipPool: () => api.get('/staking/scholarship-pool'),
}

export default stakingAPI
