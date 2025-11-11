function QuestCard({ quest, userQuest, onAccept }) {
  const questTypeColors = {
    daily: 'bg-blue-100 text-blue-800',
    weekly: 'bg-purple-100 text-purple-800',
    skill: 'bg-green-100 text-green-800',
    boss: 'bg-red-100 text-red-800',
  }

  const questTypeIcons = {
    daily: '📅',
    weekly: '📆',
    skill: '🎯',
    boss: '👑',
  }

  // Calculate progress percentage
  const calculateProgress = () => {
    if (!userQuest) return 0

    const { requirements } = quest
    const { progress } = userQuest

    let totalRequired = 0
    let totalCompleted = 0

    Object.keys(requirements).forEach((key) => {
      if (key !== 'min_score') {
        totalRequired += requirements[key]
        totalCompleted += progress[key] || 0
      }
    })

    if (totalRequired === 0) return 0
    return Math.min(Math.round((totalCompleted / totalRequired) * 100), 100)
  }

  const progressPercentage = calculateProgress()
  const isActive = userQuest && userQuest.status === 'active'
  const isCompleted = userQuest && userQuest.status === 'completed'

  return (
    <div className={`card hover:shadow-lg transition-shadow ${isCompleted ? 'opacity-60' : ''}`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{questTypeIcons[quest.quest_type]}</span>
          <h3 className="text-lg font-semibold text-gray-900">{quest.title}</h3>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${questTypeColors[quest.quest_type]}`}>
          {quest.quest_type.charAt(0).toUpperCase() + quest.quest_type.slice(1)}
        </span>
      </div>

      <p className="text-sm text-gray-600 mb-4">
        {quest.description}
      </p>

      {/* Requirements */}
      <div className="mb-4">
        <h4 className="text-xs font-semibold text-gray-700 mb-2">Requirements:</h4>
        <div className="space-y-1">
          {Object.entries(quest.requirements).map(([key, value]) => {
            const current = userQuest?.progress?.[key] || 0
            const displayKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())

            if (key === 'min_score') {
              return (
                <div key={key} className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">{displayKey}</span>
                  <span className="font-medium text-gray-900">{value}+</span>
                </div>
              )
            }

            return (
              <div key={key} className="flex items-center justify-between text-sm">
                <span className="text-gray-600">{displayKey}</span>
                <span className="font-medium text-gray-900">{current} / {value}</span>
              </div>
            )
          })}
        </div>
      </div>

      {/* Progress bar */}
      {isActive && (
        <div className="mb-4">
          <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
            <span>Progress</span>
            <span>{progressPercentage}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-green-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progressPercentage}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Rewards */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-200">
        <div className="flex items-center gap-3 text-sm">
          {quest.reward_points > 0 && (
            <span className="flex items-center gap-1 text-yellow-600 font-semibold">
              <span>⭐</span>
              {quest.reward_points} pts
            </span>
          )}
          {quest.reward_badge && (
            <span className="flex items-center gap-1 text-purple-600 font-semibold">
              <span>🏆</span>
              Badge
            </span>
          )}
        </div>

        {/* Action button */}
        {!userQuest && onAccept && (
          <button
            onClick={() => onAccept(quest.id)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold hover:bg-blue-700 transition-colors"
          >
            Accept Quest
          </button>
        )}
        {isActive && (
          <span className="px-4 py-2 bg-blue-100 text-blue-800 rounded-lg text-sm font-semibold">
            In Progress
          </span>
        )}
        {isCompleted && (
          <span className="px-4 py-2 bg-green-100 text-green-800 rounded-lg text-sm font-semibold flex items-center gap-1">
            <span>✓</span> Completed
          </span>
        )}
      </div>
    </div>
  )
}

export default QuestCard
