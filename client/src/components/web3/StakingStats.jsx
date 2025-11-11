function StakingStats({ stats }) {
  const {
    totalStaked = '0',
    activeCommitments = 0,
    completedCommitments = 0,
    scholarshipPool = '0',
    successRate = 0,
    totalRewards = '0',
  } = stats

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
      {/* Total Staked */}
      <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white">
        <div className="flex items-center justify-between mb-2">
          <span className="text-3xl">💰</span>
          <span className="text-sm opacity-80">Your Stakes</span>
        </div>
        <div className="mt-4">
          <p className="text-3xl font-bold">{totalStaked} ETH</p>
          <p className="text-sm opacity-80 mt-1">Total Staked</p>
        </div>
      </div>

      {/* Active Commitments */}
      <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-6 text-white">
        <div className="flex items-center justify-between mb-2">
          <span className="text-3xl">🔥</span>
          <span className="text-sm opacity-80">In Progress</span>
        </div>
        <div className="mt-4">
          <p className="text-3xl font-bold">{activeCommitments}</p>
          <p className="text-sm opacity-80 mt-1">Active Commitments</p>
        </div>
      </div>

      {/* Success Rate */}
      <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg p-6 text-white">
        <div className="flex items-center justify-between mb-2">
          <span className="text-3xl">📊</span>
          <span className="text-sm opacity-80">Performance</span>
        </div>
        <div className="mt-4">
          <p className="text-3xl font-bold">{successRate}%</p>
          <p className="text-sm opacity-80 mt-1">Success Rate</p>
        </div>
      </div>

      {/* Completed Commitments */}
      <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
        <div className="flex items-center gap-3 mb-3">
          <span className="text-3xl">✅</span>
          <span className="text-sm text-gray-600">Completed</span>
        </div>
        <p className="text-2xl font-bold text-gray-900">{completedCommitments}</p>
        <p className="text-sm text-gray-500 mt-1">Total Completions</p>
      </div>

      {/* Total Rewards */}
      <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
        <div className="flex items-center gap-3 mb-3">
          <span className="text-3xl">🎁</span>
          <span className="text-sm text-gray-600">Earned</span>
        </div>
        <p className="text-2xl font-bold text-gray-900">{totalRewards} ETH</p>
        <p className="text-sm text-gray-500 mt-1">Total Rewards</p>
      </div>

      {/* Scholarship Pool */}
      <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl shadow-lg p-6 text-white">
        <div className="flex items-center justify-between mb-2">
          <span className="text-3xl">🎓</span>
          <span className="text-sm opacity-80">Community</span>
        </div>
        <div className="mt-4">
          <p className="text-3xl font-bold">{scholarshipPool} ETH</p>
          <p className="text-sm opacity-80 mt-1">Scholarship Pool</p>
        </div>
      </div>
    </div>
  )
}

export default StakingStats
