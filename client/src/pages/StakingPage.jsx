import { useState, useEffect } from 'react'
import { useAddress } from '@thirdweb-dev/react'
import StakingCard from '../components/web3/StakingCard'
import CommitmentCard from '../components/web3/CommitmentCard'
import StakingStats from '../components/web3/StakingStats'

// Mock data for demonstration
const MOCK_STATS = {
  totalStaked: '0.156',
  activeCommitments: 2,
  completedCommitments: 5,
  scholarshipPool: '2.45',
  successRate: 83,
  totalRewards: '0.089',
}

const MOCK_COMMITMENTS = [
  {
    id: 1,
    amount: '0.05',
    goalType: 'streak',
    duration: 7,
    progress: 5,
    startDate: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    endDate: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(),
    status: 'active',
    daysRemaining: 2,
    canClaim: false,
  },
  {
    id: 2,
    amount: '0.03',
    goalType: 'lessons',
    duration: 14,
    progress: 10,
    startDate: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
    endDate: new Date(Date.now() + 4 * 24 * 60 * 60 * 1000).toISOString(),
    status: 'active',
    daysRemaining: 4,
    canClaim: false,
  },
  {
    id: 3,
    amount: '0.02',
    goalType: 'practice',
    duration: 7,
    progress: 7,
    startDate: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    endDate: new Date().toISOString(),
    status: 'completed',
    daysRemaining: 0,
    canClaim: true,
  },
]

function StakingPage() {
  const address = useAddress()
  const [commitments, setCommitments] = useState(MOCK_COMMITMENTS)
  const [stats, setStats] = useState(MOCK_STATS)
  const [filter, setFilter] = useState('all')

  const handleStake = async (stakeData) => {
    console.log('Creating commitment:', stakeData)

    // Simulate commitment creation
    const newCommitment = {
      id: commitments.length + 1,
      amount: stakeData.amount,
      goalType: stakeData.goalType,
      duration: stakeData.duration,
      progress: 0,
      startDate: new Date().toISOString(),
      endDate: new Date(Date.now() + stakeData.duration * 24 * 60 * 60 * 1000).toISOString(),
      status: 'active',
      daysRemaining: stakeData.duration,
      canClaim: false,
    }

    setCommitments([newCommitment, ...commitments])

    // Update stats
    setStats({
      ...stats,
      totalStaked: (parseFloat(stats.totalStaked) + parseFloat(stakeData.amount)).toFixed(3),
      activeCommitments: stats.activeCommitments + 1,
    })

    alert('✅ Commitment created successfully!')
  }

  const handleClaim = async (commitmentId) => {
    console.log('Claiming rewards for commitment:', commitmentId)

    const commitment = commitments.find(c => c.id === commitmentId)
    if (!commitment) return

    // Update commitment status
    setCommitments(commitments.map(c =>
      c.id === commitmentId ? { ...c, status: 'claimed', canClaim: false } : c
    ))

    // Update stats
    const reward = parseFloat(commitment.amount) * 1.2 // 20% reward
    setStats({
      ...stats,
      totalRewards: (parseFloat(stats.totalRewards) + reward - parseFloat(commitment.amount)).toFixed(3),
      completedCommitments: stats.completedCommitments + 1,
      activeCommitments: stats.activeCommitments - 1,
    })

    alert(`🎉 Claimed ${commitment.amount} ETH stake + rewards!`)
  }

  const filteredCommitments = commitments.filter(c => {
    if (filter === 'all') return true
    if (filter === 'active') return c.status === 'active'
    if (filter === 'completed') return c.status === 'completed'
    if (filter === 'failed') return c.status === 'failed'
    return true
  })

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

      {/* Stats Section */}
      <StakingStats stats={stats} />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column - Create Commitment */}
        <div className="lg:col-span-1">
          <StakingCard onStake={handleStake} />
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
            {filteredCommitments.length === 0 ? (
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
                {filteredCommitments.map((commitment) => (
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
                <p><strong>Earn rewards</strong> - Get your stake back plus 20% rewards when you succeed</p>
              </div>
              <div className="flex gap-3">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">4</span>
                <p><strong>Support others</strong> - Failed commitments fund scholarships for other learners</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default StakingPage
