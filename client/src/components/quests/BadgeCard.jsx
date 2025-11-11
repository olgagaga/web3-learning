function BadgeCard({ userBadge }) {
  const { badge, minted_at } = userBadge

  const badgeTypeColors = {
    mastery: 'from-yellow-400 to-orange-500',
    achievement: 'from-blue-400 to-purple-500',
    special: 'from-pink-400 to-red-500',
  }

  const badgeTypeIcons = {
    mastery: '🎓',
    achievement: '🏆',
    special: '⭐',
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  return (
    <div className="card hover:shadow-lg transition-shadow">
      {/* Badge icon with gradient background */}
      <div className={`w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-br ${badgeTypeColors[badge.badge_type]} flex items-center justify-center text-4xl shadow-lg`}>
        {badgeTypeIcons[badge.badge_type]}
      </div>

      {/* Badge name and level */}
      <div className="text-center mb-3">
        <h3 className="text-lg font-semibold text-gray-900">{badge.name}</h3>
        {badge.skill_level && (
          <span className="text-sm text-gray-500">{badge.skill_level}</span>
        )}
      </div>

      {/* Description */}
      <p className="text-sm text-gray-600 text-center mb-4">
        {badge.description}
      </p>

      {/* Badge type tag */}
      <div className="flex items-center justify-center gap-2 mb-3">
        <span className={`px-3 py-1 rounded-full text-xs font-semibold capitalize bg-gradient-to-r ${badgeTypeColors[badge.badge_type]} text-white`}>
          {badge.badge_type}
        </span>
      </div>

      {/* Earned date */}
      <div className="text-center text-xs text-gray-500 pt-3 border-t border-gray-200">
        Earned on {formatDate(minted_at)}
      </div>

      {/* Web3 indicator if applicable */}
      {userBadge.transaction_hash && (
        <div className="mt-2 flex items-center justify-center gap-1 text-xs text-purple-600">
          <span>🔗</span>
          <span>On-chain verified</span>
        </div>
      )}
    </div>
  )
}

export default BadgeCard
