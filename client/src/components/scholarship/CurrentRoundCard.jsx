function CurrentRoundCard({ round }) {
  const {
    matching_pool,
    total_donations,
    end_time,
    learner_count,
    donor_count,
    claim_count,
  } = round

  const totalPool = parseFloat(matching_pool) + parseFloat(total_donations)
  const endDate = new Date(end_time)
  const now = new Date()
  const daysRemaining = Math.max(0, Math.ceil((endDate - now) / (1000 * 60 * 60 * 24)))
  const isActive = daysRemaining > 0

  return (
    <div className="bg-gradient-to-br from-green-500 to-teal-600 rounded-xl shadow-2xl p-8 text-white">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-3xl font-bold mb-2">Current Scholarship Round</h2>
          <p className="text-green-100">
            Supporting learners with verifiable improvement
          </p>
        </div>
        <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center">
          <span className="text-4xl">💸</span>
        </div>
      </div>

      {/* Pool Info */}
      <div className="grid grid-cols-2 gap-6 mb-6">
        <div className="bg-white/10 rounded-lg p-4">
          <p className="text-green-100 text-sm mb-1">Total Pool</p>
          <p className="text-4xl font-bold">{totalPool.toFixed(3)} ETH</p>
        </div>
        <div className="bg-white/10 rounded-lg p-4">
          <p className="text-green-100 text-sm mb-1">
            {isActive ? 'Days Remaining' : 'Ended'}
          </p>
          <p className="text-4xl font-bold">{isActive ? daysRemaining : '0'}</p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-3 gap-4">
        <div className="text-center">
          <p className="text-3xl font-bold">{learner_count}</p>
          <p className="text-green-100 text-sm">Learners</p>
        </div>
        <div className="text-center">
          <p className="text-3xl font-bold">{donor_count}</p>
          <p className="text-green-100 text-sm">Donors</p>
        </div>
        <div className="text-center">
          <p className="text-3xl font-bold">{claim_count}</p>
          <p className="text-green-100 text-sm">Claims</p>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mt-6 pt-6 border-t border-white/20">
        <div className="flex justify-between text-sm mb-2">
          <span className="text-green-100">Community Donations</span>
          <span className="font-semibold">{total_donations} ETH</span>
        </div>
        <div className="w-full bg-white/20 rounded-full h-3">
          <div
            className="bg-white rounded-full h-3 transition-all duration-500"
            style={{
              width: `${Math.min((parseFloat(total_donations) / parseFloat(matching_pool)) * 100, 100)}%`,
            }}
          />
        </div>
        <div className="flex justify-between text-sm mt-2">
          <span className="text-green-100">Platform Matching</span>
          <span className="font-semibold">{matching_pool} ETH</span>
        </div>
      </div>
    </div>
  )
}

export default CurrentRoundCard
