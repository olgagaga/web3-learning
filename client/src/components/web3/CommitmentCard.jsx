function CommitmentCard({ commitment, onClaim, onWithdraw }) {
  const {
    id,
    amount,
    goalType,
    duration,
    progress,
    startDate,
    endDate,
    status,
    daysRemaining,
    canClaim,
  } = commitment

  const progressPercentage = (progress / duration) * 100

  const getStatusColor = () => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'completed':
        return 'bg-blue-100 text-blue-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getGoalIcon = () => {
    switch (goalType) {
      case 'streak':
        return '🔥'
      case 'lessons':
        return '📚'
      case 'score':
        return '🎯'
      case 'practice':
        return '⏱️'
      default:
        return '🎯'
    }
  }

  const getGoalLabel = () => {
    switch (goalType) {
      case 'streak':
        return 'Daily Streak'
      case 'lessons':
        return 'Complete Lessons'
      case 'score':
        return 'Achieve Score'
      case 'practice':
        return 'Practice Hours'
      default:
        return goalType
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200 hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
            <span className="text-2xl">{getGoalIcon()}</span>
          </div>
          <div>
            <h4 className="font-bold text-gray-900">{getGoalLabel()}</h4>
            <p className="text-sm text-gray-500">{duration} days commitment</p>
          </div>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor()}`}>
          {status.toUpperCase()}
        </span>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex justify-between text-sm mb-2">
          <span className="text-gray-600 font-medium">Progress</span>
          <span className="text-gray-900 font-semibold">
            {progress}/{duration} days
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all duration-300 ${
              progressPercentage >= 100
                ? 'bg-green-500'
                : progressPercentage >= 50
                ? 'bg-blue-500'
                : 'bg-yellow-500'
            }`}
            style={{ width: `${Math.min(progressPercentage, 100)}%` }}
          />
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-gray-50 rounded-lg p-3">
          <p className="text-xs text-gray-500 mb-1">Staked Amount</p>
          <p className="text-lg font-bold text-gray-900">{amount} ETH</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-3">
          <p className="text-xs text-gray-500 mb-1">Days Remaining</p>
          <p className="text-lg font-bold text-gray-900">{daysRemaining}</p>
        </div>
      </div>

      {/* Dates */}
      <div className="flex justify-between text-xs text-gray-500 mb-4 pb-4 border-b border-gray-200">
        <div>
          <span className="font-semibold">Start:</span> {new Date(startDate).toLocaleDateString()}
        </div>
        <div>
          <span className="font-semibold">End:</span> {new Date(endDate).toLocaleDateString()}
        </div>
      </div>

      {/* Actions */}
      {status === 'completed' && canClaim && (
        <button
          onClick={() => onClaim(id)}
          className="w-full py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition-colors"
        >
          🎉 Claim Rewards + Stake
        </button>
      )}

      {status === 'failed' && (
        <div className="text-center py-3 bg-red-50 rounded-lg">
          <p className="text-sm text-red-800 font-medium">
            Commitment failed. Stake sent to scholarship pool.
          </p>
        </div>
      )}

      {status === 'active' && (
        <div className="text-center py-2">
          <p className="text-sm text-gray-600">
            Keep going! Complete your daily activities to maintain your streak.
          </p>
        </div>
      )}
    </div>
  )
}

export default CommitmentCard
