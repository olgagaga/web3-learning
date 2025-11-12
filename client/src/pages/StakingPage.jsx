import { useState, useEffect } from 'react'
import { useAddress, useContract, useContractWrite } from '@thirdweb-dev/react'
import { ethers } from 'ethers'
import StakingCard from '../components/web3/StakingCard'
import CommitmentCard from '../components/web3/CommitmentCard'
import StakingStats from '../components/web3/StakingStats'
import stakingAPI from '../services/stakingAPI'

const CONTRACT_ADDRESS = import.meta.env.VITE_STAKING_CONTRACT_ADDRESS

function StakingPage() {
  const address = useAddress()
  const { contract } = useContract(CONTRACT_ADDRESS)
  const { mutateAsync: createCommitmentContract } = useContractWrite(contract, 'createCommitment')
  const { mutateAsync: claimRewardContract } = useContractWrite(contract, 'claimReward')

  const [commitments, setCommitments] = useState([])
  const [stats, setStats] = useState(null)
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)

  // Load data on mount and when wallet connects
  useEffect(() => {
    if (address) {
      loadData()
      // Connect wallet to backend
      stakingAPI.connectWallet({
        wallet_address: address,
        wallet_provider: 'thirdweb',
      }).catch(err => console.error('Wallet sync error:', err))
    } else {
      setCommitments([])
      setStats(null)
      setLoading(false)
    }
  }, [address])

  const loadData = async () => {
    setLoading(true)
    try {
      const [commitmentsRes, dashboardRes] = await Promise.all([
        stakingAPI.getMyCommitments(),
        stakingAPI.getDashboard(),
      ])

      setCommitments(commitmentsRes.data || [])
      setStats(dashboardRes.data || {})
    } catch (error) {
      console.error('Failed to load staking data:', error)
      // Set empty defaults on error
      setCommitments([])
      setStats({
        total_staked: '0',
        active_commitments: 0,
        success_rate: 0,
        total_rewards_earned: '0',
        completed_commitments: 0,
        failed_commitments: 0,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleStake = async (stakeData) => {
    if (!address || !contract) {
      alert('Please connect your wallet first')
      return
    }

    setCreating(true)
    try {
      console.log('Creating commitment:', stakeData)

      // Map goal type to commitment type
      const commitmentTypeMap = {
        'streak': 'streak_7_day',
        'lessons': 'reading_goal',
        'score': 'writing_goal',
        'practice': 'streak_30_day',
      }

      // 1. Create commitment on smart contract
      const targetValue = stakeData.duration // For streaks, target = duration
      const durationDays = stakeData.duration

      console.log('Calling smart contract...')
      const tx = await createCommitmentContract({
        args: [targetValue, durationDays],
        overrides: {
          value: ethers.utils.parseEther(stakeData.amount.toString()),
        },
      })

      console.log('Transaction:', tx)

      // 2. Save to backend
      console.log('Saving to backend...')
      await stakingAPI.createCommitment({
        commitment_type: commitmentTypeMap[stakeData.goalType] || 'streak_7_day',
        target_value: targetValue,
        duration_days: durationDays,
        stake_amount: stakeData.amount,
        stake_tx_hash: tx.receipt.transactionHash,
        contract_address: CONTRACT_ADDRESS,
      })

      // 3. Reload data
      await loadData()

      alert('✅ Commitment created successfully!')
    } catch (error) {
      console.error('Failed to create commitment:', error)
      alert(`❌ Failed to create commitment: ${error.message || 'Unknown error'}`)
    } finally {
      setCreating(false)
    }
  }

  const handleClaim = async (commitmentId) => {
    if (!address || !contract) {
      alert('Please connect your wallet first')
      return
    }

    try {
      console.log('Claiming rewards for commitment:', commitmentId)

      // Get commitment details
      const commitment = commitments.find(c => c.id === commitmentId)
      if (!commitment) {
        alert('Commitment not found')
        return
      }

      // Call smart contract to claim reward
      console.log('Calling claimReward on contract...')
      const tx = await claimRewardContract({
        args: [commitment.contract_commitment_id || commitmentId],
      })

      console.log('Claim transaction:', tx)

      // Update backend
      await stakingAPI.claimReward(commitmentId, tx.receipt.transactionHash)

      // Reload data
      await loadData()

      alert('🎉 Rewards claimed successfully!')
    } catch (error) {
      console.error('Failed to claim rewards:', error)
      alert(`❌ Failed to claim rewards: ${error.message || 'Unknown error'}`)
    }
  }

  const filteredCommitments = commitments.filter(c => {
    if (filter === 'all') return true
    if (filter === 'active') return c.status === 'active'
    if (filter === 'completed') return c.status === 'completed' || c.status === 'claimed'
    if (filter === 'failed') return c.status === 'failed'
    return true
  })

  // Transform backend data to component format
  const transformedCommitments = filteredCommitments.map(c => ({
    id: c.id,
    amount: c.stake_amount,
    goalType: c.commitment_type?.includes('streak') ? 'streak' :
              c.commitment_type?.includes('reading') ? 'lessons' :
              c.commitment_type?.includes('writing') ? 'score' : 'practice',
    duration: c.duration_days,
    progress: c.progress,
    startDate: c.created_at,
    endDate: c.deadline,
    status: c.status,
    daysRemaining: Math.max(0, Math.ceil((new Date(c.deadline) - new Date()) / (1000 * 60 * 60 * 24))),
    canClaim: c.status === 'completed' && !c.reward_claimed,
  }))

  const transformedStats = stats ? {
    totalStaked: parseFloat(stats.total_staked || 0).toFixed(3),
    activeCommitments: stats.active_commitments || 0,
    completedCommitments: stats.completed_commitments || 0,
    scholarshipPool: parseFloat(stats.scholarship_pool_balance || 0).toFixed(3),
    successRate: stats.success_rate || 0,
    totalRewards: parseFloat(stats.total_rewards_earned || 0).toFixed(3),
  } : null

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Commitment Staking
        </h1>
        <p className="text-gray-600">
          Stake tokens to commit to your learning goals and earn rewards
        </p>
      </div>

      {/* Connection Warning */}
      {!address && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-8">
          <div className="flex">
            <div className="flex-shrink-0">
              <span className="text-2xl">⚠️</span>
            </div>
            <div className="ml-3">
              <p className="text-sm text-yellow-700">
                <span className="font-semibold">Wallet not connected.</span> Please connect your wallet to create commitments and view your stakes.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && address && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          <p className="mt-4 text-gray-600">Loading your commitments...</p>
        </div>
      )}

      {/* Content */}
      {!loading && address && (
        <>
          {/* Stats Section */}
          {transformedStats && <StakingStats stats={transformedStats} />}

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Column - Create Commitment */}
            <div className="lg:col-span-1">
              <StakingCard onStake={handleStake} disabled={creating} />
              {creating && (
                <p className="text-center text-sm text-gray-500 mt-2">
                  Creating commitment...
                </p>
              )}
            </div>

            {/* Right Column - Active Commitments */}
            <div className="lg:col-span-2">
              <div className="mb-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold text-gray-900">Your Commitments</h2>

                  {/* Filter Buttons */}
                  <div className="flex gap-2">
                    {['all', 'active', 'completed'].map((f) => (
                      <button
                        key={f}
                        onClick={() => setFilter(f)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                          filter === f
                            ? 'bg-primary text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {f.charAt(0).toUpperCase() + f.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Commitments List */}
                {transformedCommitments.length === 0 ? (
                  <div className="bg-white rounded-xl shadow-md p-12 text-center border border-gray-200">
                    <span className="text-6xl mb-4 block">📭</span>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      No commitments found
                    </h3>
                    <p className="text-gray-500">
                      {filter === 'all'
                        ? 'Create your first commitment to get started!'
                        : `No ${filter} commitments at this time.`}
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {transformedCommitments.map((commitment) => (
                      <CommitmentCard
                        key={commitment.id}
                        commitment={commitment}
                        onClaim={handleClaim}
                      />
                    ))}
                  </div>
                )}
              </div>

              {/* How It Works Section */}
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200 mt-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">
                  🎯 How Commitment Staking Works
                </h3>
                <div className="space-y-3 text-sm text-gray-700">
                  <div className="flex gap-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">1</span>
                    <p><strong>Stake tokens</strong> - Choose your goal type and commit tokens for a specific duration</p>
                  </div>
                  <div className="flex gap-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">2</span>
                    <p><strong>Complete daily activities</strong> - Practice reading, writing, or complete quests daily</p>
                  </div>
                  <div className="flex gap-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">3</span>
                    <p><strong>Earn rewards</strong> - Get your stake back plus 10% bonus when you succeed</p>
                  </div>
                  <div className="flex gap-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">4</span>
                    <p><strong>Support others</strong> - Failed commitments fund scholarships for other learners</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default StakingPage
