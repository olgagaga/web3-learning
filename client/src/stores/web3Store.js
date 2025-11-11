import { create } from 'zustand'

export const useWeb3Store = create((set) => ({
  // Wallet connection state
  address: null,
  isConnected: false,
  balance: '0',

  // Staking state
  userStakes: [],
  totalStaked: '0',
  availableRewards: '0',

  // Contract state
  contractAddress: import.meta.env.VITE_STAKING_CONTRACT_ADDRESS,

  // Actions
  setWallet: (address, balance) => set({
    address,
    isConnected: !!address,
    balance
  }),

  setStakingData: (data) => set({
    userStakes: data.stakes || [],
    totalStaked: data.totalStaked || '0',
    availableRewards: data.rewards || '0'
  }),

  disconnect: () => set({
    address: null,
    isConnected: false,
    balance: '0',
    userStakes: [],
    totalStaked: '0',
    availableRewards: '0'
  }),
}))
