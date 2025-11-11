import { useState, useEffect } from 'react'
import { questsAPI } from '../services/questsAPI'
import BadgeCard from '../components/quests/BadgeCard'

function BadgesPage() {
  const [showcase, setShowcase] = useState(null)
  const [allBadges, setAllBadges] = useState([])
  const [earnedBadgeIds, setEarnedBadgeIds] = useState(new Set())
  const [badgeProgress, setBadgeProgress] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadData()

    // Reload data when user comes back to this page
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        loadData()
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)

    // Cleanup
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)

      const [showcaseRes, allBadgesRes, progressRes] = await Promise.all([
        questsAPI.getBadgeShowcase(),
        questsAPI.getAllBadges(),
        questsAPI.getAllBadgesProgress()
      ])

      setShowcase(showcaseRes.data)
      setAllBadges(allBadgesRes.data)
      setBadgeProgress(progressRes.data)

      // Create a set of earned badge IDs for quick lookup
      const earnedIds = new Set()
      Object.values(showcaseRes.data.badges_by_category).forEach(category => {
        category.forEach(badge => earnedIds.add(badge.id))
      })
      setEarnedBadgeIds(earnedIds)

    } catch (err) {
      console.error('Error loading badges:', err)
      setError('Failed to load badges. Please try again.')
    } finally {
      setLoading(false)
    }
  }

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

  const UnearnedBadgeCard = ({ badge }) => {
    const progress = badgeProgress[badge.id] || { progress: 0, criteria_progress: {} }

    return (
      <div className="card hover:shadow-lg transition-shadow relative">
        {/* Badge Icon */}
        <div className={`w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-br ${badgeTypeColors[badge.badge_type]} flex items-center justify-center text-4xl shadow-lg opacity-40`}>
          {badgeTypeIcons[badge.badge_type]}
        </div>

        {/* Badge Info */}
        <div className="text-center mb-3">
          <h3 className="text-lg font-semibold text-gray-900">{badge.name}</h3>
          {badge.skill_level && (
            <span className="text-sm text-gray-500 capitalize">{badge.skill_level}</span>
          )}
        </div>

        <p className="text-sm text-gray-600 text-center mb-4 line-clamp-2">
          {badge.description}
        </p>

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-gray-700">Progress</span>
            <span className="text-xs font-bold text-blue-600">{Math.round(progress.progress)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div
              className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
              style={{ width: `${progress.progress}%` }}
            ></div>
          </div>
        </div>

        {/* Criteria Progress */}
        {Object.keys(progress.criteria_progress).length > 0 && (
          <div className="pt-3 border-t border-gray-200">
            <p className="text-xs font-semibold text-gray-700 mb-2">Requirements:</p>
            <div className="space-y-2">
              {progress.criteria_progress.reading_accuracy && (
                <div className="text-xs">
                  <div className="flex justify-between text-gray-600">
                    <span>Reading Accuracy</span>
                    <span className="font-semibold">
                      {progress.criteria_progress.reading_accuracy.current}% / {progress.criteria_progress.reading_accuracy.required}%
                    </span>
                  </div>
                  <div className="text-gray-500 text-[10px]">
                    {progress.criteria_progress.reading_accuracy.items_completed} / {progress.criteria_progress.reading_accuracy.items_required} items
                  </div>
                </div>
              )}
              {progress.criteria_progress.writing_avg_score && (
                <div className="text-xs">
                  <div className="flex justify-between text-gray-600">
                    <span>Writing Average</span>
                    <span className="font-semibold">
                      {progress.criteria_progress.writing_avg_score.current} / {progress.criteria_progress.writing_avg_score.required}
                    </span>
                  </div>
                  <div className="text-gray-500 text-[10px]">
                    {progress.criteria_progress.writing_avg_score.essays_written} / {progress.criteria_progress.writing_avg_score.essays_required} essays
                  </div>
                </div>
              )}
              {progress.criteria_progress.min_score && (
                <div className="text-xs">
                  <div className="flex justify-between text-gray-600">
                    <span>Best Essay Score</span>
                    <span className="font-semibold">
                      {progress.criteria_progress.min_score.current} / {progress.criteria_progress.min_score.required}
                    </span>
                  </div>
                </div>
              )}
              {progress.criteria_progress.quests_completed && (
                <div className="text-xs">
                  <div className="flex justify-between text-gray-600">
                    <span>Quests Completed</span>
                    <span className="font-semibold">
                      {progress.criteria_progress.quests_completed.current} / {progress.criteria_progress.quests_completed.required}
                    </span>
                  </div>
                </div>
              )}
              {progress.criteria_progress.weekly_quests && (
                <div className="text-xs">
                  <div className="flex justify-between text-gray-600">
                    <span>Weekly Quests</span>
                    <span className="font-semibold">
                      {progress.criteria_progress.weekly_quests.current} / {progress.criteria_progress.weekly_quests.required}
                    </span>
                  </div>
                </div>
              )}
              {progress.criteria_progress.boss_reading && (
                <div className="text-xs">
                  <div className="flex justify-between text-gray-600">
                    <span>Reading Boss</span>
                    <span className="font-semibold">
                      {progress.criteria_progress.boss_reading.current} / {progress.criteria_progress.boss_reading.required}
                    </span>
                  </div>
                </div>
              )}
              {progress.criteria_progress.boss_writing && (
                <div className="text-xs">
                  <div className="flex justify-between text-gray-600">
                    <span>Writing Boss</span>
                    <span className="font-semibold">
                      {progress.criteria_progress.boss_writing.current} / {progress.criteria_progress.boss_writing.required}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Lock Icon */}
        <div className="absolute top-3 right-3">
          <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
            <span className="text-lg">🔒</span>
          </div>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading badges...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card bg-red-50">
        <p className="text-red-600">{error}</p>
        <button
          onClick={loadData}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Try Again
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Badge Collection</h1>
          <p className="text-gray-600 mt-2">Earn badges by completing quests and achieving milestones</p>
        </div>
        <button
          onClick={loadData}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          <svg className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>

      {/* Stats Overview */}
      {showcase && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="card bg-gradient-to-br from-purple-50 to-purple-100">
            <div className="text-3xl mb-2">🏆</div>
            <div className="text-2xl font-bold text-gray-900">{showcase.total_badges}</div>
            <div className="text-sm text-gray-600">Total Badges</div>
          </div>
          <div className="card bg-gradient-to-br from-yellow-50 to-yellow-100">
            <div className="text-3xl mb-2">🎓</div>
            <div className="text-2xl font-bold text-gray-900">{showcase.mastery_badges}</div>
            <div className="text-sm text-gray-600">Mastery</div>
          </div>
          <div className="card bg-gradient-to-br from-blue-50 to-blue-100">
            <div className="text-3xl mb-2">🏆</div>
            <div className="text-2xl font-bold text-gray-900">{showcase.achievement_badges}</div>
            <div className="text-sm text-gray-600">Achievements</div>
          </div>
          <div className="card bg-gradient-to-br from-pink-50 to-pink-100">
            <div className="text-3xl mb-2">⭐</div>
            <div className="text-2xl font-bold text-gray-900">{showcase.special_badges}</div>
            <div className="text-sm text-gray-600">Special</div>
          </div>
        </div>
      )}

      {/* Earned Badges by Category */}
      {showcase && showcase.total_badges > 0 && (
        <div className="space-y-8">
          <h2 className="text-2xl font-bold text-gray-900">Your Earned Badges</h2>

          {/* Mastery Badges */}
          {showcase.badges_by_category.mastery.length > 0 && (
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <span>🎓</span>
                <span>Mastery Badges</span>
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {showcase.badges_by_category.mastery.map((badge) => (
                  <BadgeCard key={badge.id} userBadge={{ badge, minted_at: badge.earned_at }} />
                ))}
              </div>
            </div>
          )}

          {/* Achievement Badges */}
          {showcase.badges_by_category.achievement.length > 0 && (
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <span>🏆</span>
                <span>Achievement Badges</span>
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {showcase.badges_by_category.achievement.map((badge) => (
                  <BadgeCard key={badge.id} userBadge={{ badge, minted_at: badge.earned_at }} />
                ))}
              </div>
            </div>
          )}

          {/* Special Badges */}
          {showcase.badges_by_category.special.length > 0 && (
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <span>⭐</span>
                <span>Special Badges</span>
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {showcase.badges_by_category.special.map((badge) => (
                  <BadgeCard key={badge.id} userBadge={{ badge, minted_at: badge.earned_at }} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* All Available Badges */}
      <div className="space-y-4 pt-8 border-t border-gray-200">
        <h2 className="text-2xl font-bold text-gray-900">All Available Badges</h2>
        <p className="text-gray-600">Complete challenges to unlock these badges</p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {allBadges.map((badge) => {
            if (earnedBadgeIds.has(badge.id)) {
              // Skip already earned badges
              return null
            }

            return (
              <UnearnedBadgeCard key={badge.id} badge={badge} />
            )
          })}
        </div>
      </div>

      {/* Empty State */}
      {showcase && showcase.total_badges === 0 && (
        <div className="card text-center py-12">
          <div className="text-6xl mb-4">🏆</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No badges yet</h3>
          <p className="text-gray-600 mb-4">Start completing quests to earn your first badge!</p>
          <a
            href="/quests"
            className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            View Quests
          </a>
        </div>
      )}
    </div>
  )
}

export default BadgesPage
