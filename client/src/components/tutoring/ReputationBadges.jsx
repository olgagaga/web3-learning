function ReputationBadges({ badges }) {
  const {
    total = 0,
    essay_feedback = 0,
    speaking_practice = 0,
    reading_tutor = 0,
    writing_coach = 0,
  } = badges

  const badgeTypes = [
    {
      type: 'essay_feedback',
      count: essay_feedback,
      label: 'Essay Feedback',
      icon: '📝',
      color: 'from-blue-500 to-blue-600',
    },
    {
      type: 'speaking_practice',
      count: speaking_practice,
      label: 'Speaking Practice',
      icon: '🗣️',
      color: 'from-green-500 to-green-600',
    },
    {
      type: 'reading_tutor',
      count: reading_tutor,
      label: 'Reading Tutor',
      icon: '📖',
      color: 'from-purple-500 to-purple-600',
    },
    {
      type: 'writing_coach',
      count: writing_coach,
      label: 'Writing Coach',
      icon: '✍️',
      color: 'from-orange-500 to-orange-600',
    },
  ]

  return (
    <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 bg-gradient-to-br from-yellow-400 to-yellow-500 rounded-lg flex items-center justify-center text-2xl">
          🏆
        </div>
        <div>
          <h3 className="text-lg font-bold text-gray-900">Reputation Badges</h3>
          <p className="text-sm text-gray-500">Soulbound tokens (non-transferable)</p>
        </div>
      </div>

      {/* Total */}
      <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg p-4 mb-6 text-center">
        <p className="text-4xl font-bold text-gray-900 mb-1">{total}</p>
        <p className="text-sm text-gray-600 font-medium">Total Badges Earned</p>
      </div>

      {/* Badge Breakdown */}
      <div className="space-y-3">
        {badgeTypes.map((badge) => (
          <div
            key={badge.type}
            className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div className="flex items-center gap-3">
              <div
                className={`w-10 h-10 bg-gradient-to-br ${badge.color} rounded-lg flex items-center justify-center text-xl shadow-md`}
              >
                {badge.icon}
              </div>
              <div>
                <p className="font-semibold text-gray-900 text-sm">{badge.label}</p>
                <p className="text-xs text-gray-500">Completed sessions</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-gray-900">{badge.count}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Info */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="flex gap-2 text-xs text-gray-600">
          <span>💎</span>
          <p>
            These are <span className="font-semibold">Soulbound Tokens (SBTs)</span> - permanent,
            non-transferable credentials stored on the blockchain that prove your expertise.
          </p>
        </div>
      </div>
    </div>
  )
}

export default ReputationBadges
