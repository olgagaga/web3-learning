import { useState } from 'react'
import { useAddress } from '@thirdweb-dev/react'
import CurrentRoundCard from '../components/scholarship/CurrentRoundCard'
import DonateCard from '../components/scholarship/DonateCard'
import ImprovementClaimCard from '../components/scholarship/ImprovementClaimCard'
import LeaderboardTable from '../components/scholarship/LeaderboardTable'

// Mock data
const MOCK_CURRENT_ROUND = {
  id: 1,
  matching_pool: '1.5',
  total_donations: '0.8',
  end_time: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
  learner_count: 24,
  donor_count: 18,
  claim_count: 32,
  is_active: true,
}

const MOCK_MY_CLAIMS = [
  {
    id: 1,
    metric_type: 'reading_score',
    before_score: 65,
    after_score: 82,
    improvement_percent: 26,
    timeframe_days: 14,
    is_verified: true,
    is_rewarded: true,
    reward_amount: '0.125',
    claimed_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 2,
    metric_type: 'writing_score',
    before_score: 70,
    after_score: 85,
    improvement_percent: 21,
    timeframe_days: 10,
    is_verified: true,
    is_rewarded: false,
    reward_amount: '0',
    claimed_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
  },
]

const MOCK_TOP_IMPROVERS = [
  {
    name: 'Sarah Chen',
    metric_type: 'Reading Score',
    improvement_percent: 35,
    reward: '0.215',
  },
  {
    name: 'Michael Torres',
    metric_type: 'Writing Score',
    improvement_percent: 30,
    reward: '0.185',
  },
  {
    name: 'Emma Wilson',
    metric_type: 'Overall Score',
    improvement_percent: 28,
    reward: '0.165',
  },
  {
    name: 'David Kim',
    metric_type: 'Speaking Score',
    improvement_percent: 26,
    reward: '0.125',
  },
  {
    name: 'Alice Johnson',
    metric_type: 'Reading Score',
    improvement_percent: 25,
    reward: '0.118',
  },
]

const MOCK_TOP_DONORS = [
  {
    name: 'John Smith',
    amount: '0.25',
    learners_supported: 8,
  },
  {
    name: 'Jane Doe',
    amount: '0.18',
    learners_supported: 6,
  },
  {
    name: 'Anonymous',
    amount: '0.15',
    learners_supported: 5,
  },
  {
    name: 'Bob Johnson',
    amount: '0.12',
    learners_supported: 4,
  },
]

function ScholarshipPage() {
  const address = useAddress()
  const [activeTab, setActiveTab] = useState('dashboard')
  const [myClaims, setMyClaims] = useState(MOCK_MY_CLAIMS)
  const [myDonations, setMyDonations] = useState([])
  const [myTotalDonated, setMyTotalDonated] = useState(0)

  const handleDonate = async (donationData) => {
    console.log('Donating:', donationData)

    const newDonation = {
      id: myDonations.length + 1,
      amount: donationData.amount,
      is_anonymous: donationData.isAnonymous,
      donated_at: new Date().toISOString(),
    }

    setMyDonations([newDonation, ...myDonations])
    setMyTotalDonated(myTotalDonated + donationData.amount)

    // Update round stats (mock)
    MOCK_CURRENT_ROUND.total_donations = (
      parseFloat(MOCK_CURRENT_ROUND.total_donations) + donationData.amount
    ).toFixed(3)
    MOCK_CURRENT_ROUND.donor_count += 1

    alert(`✅ Donated ${donationData.amount} ETH successfully!`)
  }

  const myTotalRewards = myClaims
    .filter((c) => c.is_rewarded)
    .reduce((sum, c) => sum + parseFloat(c.reward_amount), 0)

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Quadratic Scholarship Pool
        </h1>
        <p className="text-gray-600">
          Earn rewards for verifiable learning improvements through community funding
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
                <span className="font-semibold">Wallet not connected.</span> Connect
                your wallet to donate or claim rewards.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Current Round Card */}
      <div className="mb-8">
        <CurrentRoundCard round={MOCK_CURRENT_ROUND} />
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-8 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('dashboard')}
          className={`px-6 py-3 font-semibold transition-colors border-b-2 ${
            activeTab === 'dashboard'
              ? 'border-primary text-primary'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          📊 Dashboard
        </button>
        <button
          onClick={() => setActiveTab('donate')}
          className={`px-6 py-3 font-semibold transition-colors border-b-2 ${
            activeTab === 'donate'
              ? 'border-primary text-primary'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          💰 Donate
        </button>
        <button
          onClick={() => setActiveTab('my-improvements')}
          className={`px-6 py-3 font-semibold transition-colors border-b-2 ${
            activeTab === 'my-improvements'
              ? 'border-primary text-primary'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          📈 My Improvements
        </button>
        <button
          onClick={() => setActiveTab('leaderboard')}
          className={`px-6 py-3 font-semibold transition-colors border-b-2 ${
            activeTab === 'leaderboard'
              ? 'border-primary text-primary'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          🏆 Leaderboard
        </button>
      </div>

      {/* Content */}
      {activeTab === 'dashboard' && (
        <div className="space-y-8">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <span className="text-3xl">🎓</span>
                <span className="text-sm text-gray-500">Your Stats</span>
              </div>
              <p className="text-3xl font-bold text-gray-900 mb-1">
                {myClaims.length}
              </p>
              <p className="text-gray-600">Claims Submitted</p>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <span className="text-3xl">💸</span>
                <span className="text-sm text-gray-500">Earned</span>
              </div>
              <p className="text-3xl font-bold text-green-600 mb-1">
                {myTotalRewards.toFixed(3)} ETH
              </p>
              <p className="text-gray-600">Total Rewards</p>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <span className="text-3xl">💰</span>
                <span className="text-sm text-gray-500">Contributed</span>
              </div>
              <p className="text-3xl font-bold text-blue-600 mb-1">
                {myTotalDonated.toFixed(3)} ETH
              </p>
              <p className="text-gray-600">Total Donated</p>
            </div>
          </div>

          {/* How It Works */}
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              💡 How Quadratic Funding Works
            </h3>
            <div className="grid md:grid-cols-2 gap-6 text-sm text-gray-700">
              <div className="space-y-3">
                <div className="flex gap-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
                    1
                  </span>
                  <p>
                    <strong>Community Donates:</strong> Many small donations create a
                    larger matching pool
                  </p>
                </div>
                <div className="flex gap-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
                    2
                  </span>
                  <p>
                    <strong>Learners Improve:</strong> Submit verifiable improvement
                    (min 10%, 7+ days)
                  </p>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex gap-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
                    3
                  </span>
                  <p>
                    <strong>Platform Verifies:</strong> Attestation confirms genuine
                    improvement
                  </p>
                </div>
                <div className="flex gap-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
                    4
                  </span>
                  <p>
                    <strong>Rewards Distributed:</strong> QF algorithm favors broad
                    community support
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'donate' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <DonateCard onDonate={handleDonate} />

          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
              <h3 className="text-lg font-bold text-gray-900 mb-4">
                Why Donate?
              </h3>
              <div className="space-y-3 text-sm text-gray-700">
                <div className="flex gap-3 items-start">
                  <span className="text-xl">🎯</span>
                  <p>
                    <strong>Impact:</strong> Support learners with verified improvements
                  </p>
                </div>
                <div className="flex gap-3 items-start">
                  <span className="text-xl">🔍</span>
                  <p>
                    <strong>Transparency:</strong> All distributions are public and
                    verifiable
                  </p>
                </div>
                <div className="flex gap-3 items-start">
                  <span className="text-xl">📈</span>
                  <p>
                    <strong>Amplified:</strong> Platform matching multiplies your
                    contribution
                  </p>
                </div>
                <div className="flex gap-3 items-start">
                  <span className="text-xl">🤝</span>
                  <p>
                    <strong>Community:</strong> Join other donors supporting education
                  </p>
                </div>
              </div>
            </div>

            {myDonations.length > 0 && (
              <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
                <h3 className="text-lg font-bold text-gray-900 mb-4">
                  My Donations
                </h3>
                <div className="space-y-3">
                  {myDonations.map((donation) => (
                    <div
                      key={donation.id}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                    >
                      <div>
                        <p className="font-semibold text-gray-900">
                          {donation.amount} ETH
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(donation.donated_at).toLocaleDateString()}
                        </p>
                      </div>
                      {donation.is_anonymous && (
                        <span className="text-xs text-gray-500 italic">
                          Anonymous
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'my-improvements' && (
        <div>
          <div className="mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-2">
              My Improvement Claims
            </h2>
            <p className="text-sm text-gray-600">
              Track your learning progress and rewards
            </p>
          </div>

          {myClaims.length === 0 ? (
            <div className="bg-white rounded-xl shadow-md p-12 text-center border border-gray-200">
              <span className="text-6xl mb-4 block">📈</span>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                No claims yet
              </h3>
              <p className="text-gray-500 mb-6">
                Keep learning and improving to earn scholarship rewards!
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {myClaims.map((claim) => (
                <ImprovementClaimCard key={claim.id} claim={claim} />
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'leaderboard' && (
        <div className="space-y-8">
          <LeaderboardTable
            data={MOCK_TOP_IMPROVERS}
            title="🏆 Top Improvers This Round"
            type="improvers"
          />

          <LeaderboardTable
            data={MOCK_TOP_DONORS}
            title="💝 Top Donors This Round"
            type="donors"
          />
        </div>
      )}
    </div>
  )
}

export default ScholarshipPage
