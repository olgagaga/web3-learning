function ImprovementClaimCard({ claim, onViewDetails }) {
  const {
    id,
    metric_type,
    before_score,
    after_score,
    improvement_percent,
    timeframe_days,
    is_verified,
    is_rewarded,
    reward_amount,
    claimed_at,
  } = claim

  const getMetricIcon = () => {
    switch (metric_type) {
      case 'reading_score':
        return '📖'
      case 'writing_score':
        return '✍️'
      case 'speaking_score':
        return '🗣️'
      case 'overall_score':
        return '📊'
      case 'quest_completion':
        return '🎯'
      case 'streak_days':
        return '🔥'
      default:
        return '📈'
    }
  }

  const getMetricLabel = () => {
    return metric_type.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())
  }

  const getStatusBadge = () => {
    if (is_rewarded) {
      return <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">REWARDED</span>
    }
    if (is_verified) {
      return <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-semibold">VERIFIED</span>
    }
    return <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-semibold">PENDING</span>
  }

  return (
    <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200 hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-2xl">
            {getMetricIcon()}
          </div>
          <div>
            <h3 className="font-bold text-lg text-gray-900">{getMetricLabel()}</h3>
            <p className="text-sm text-gray-500">{timeframe_days} days of improvement</p>
          </div>
        </div>
        {getStatusBadge()}
      </div>

      {/* Improvement Stats */}
      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <p className="text-2xl font-bold text-gray-900">{before_score}</p>
          <p className="text-xs text-gray-500">Before</p>
        </div>
        <div className="flex items-center justify-center">
          <div className="text-center">
            <p className="text-2xl font-bold text-green-600">+{improvement_percent}%</p>
            <p className="text-xs text-gray-500">Improvement</p>
          </div>
        </div>
        <div className="text-center p-3 bg-green-50 rounded-lg">
          <p className="text-2xl font-bold text-green-600">{after_score}</p>
          <p className="text-xs text-gray-500">After</p>
        </div>
      </div>

      {/* Reward Info */}
      {is_rewarded && (
        <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-lg p-4 mb-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-700 font-semibold">Reward Earned</p>
              <p className="text-xs text-gray-600">Via Quadratic Funding</p>
            </div>
            <p className="text-2xl font-bold text-gray-900">{reward_amount} ETH</p>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500">
          Claimed {new Date(claimed_at).toLocaleDateString()}
        </p>
        {!is_verified && (
          <span className="text-xs text-yellow-600 font-medium">
            Awaiting verification
          </span>
        )}
      </div>
    </div>
  )
}

export default ImprovementClaimCard
