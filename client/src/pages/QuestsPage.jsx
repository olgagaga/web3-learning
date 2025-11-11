import { useState, useEffect } from 'react'
import { questsAPI } from '../services/questsAPI'
import QuestCard from '../components/quests/QuestCard'
import BadgeCard from '../components/quests/BadgeCard'

function QuestsPage() {
  const [activeTab, setActiveTab] = useState('available') // available, active, completed, badges
  const [allQuests, setAllQuests] = useState([])
  const [userQuests, setUserQuests] = useState([])
  const [badges, setBadges] = useState([])
  const [stats, setStats] = useState(null)
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

      const [questsRes, myQuestsRes, badgesRes, statsRes] = await Promise.all([
        questsAPI.getAllQuests(),
        questsAPI.getMyQuests(),
        questsAPI.getBadges(),
        questsAPI.getStats(),
      ])

      setAllQuests(questsRes.data)
      setUserQuests(myQuestsRes.data)
      setBadges(badgesRes.data)
      setStats(statsRes.data)
    } catch (err) {
      console.error('Error loading quests:', err)
      setError('Failed to load quests. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleAcceptQuest = async (questId) => {
    try {
      const response = await questsAPI.acceptQuest(questId)
      setUserQuests([...userQuests, response.data])
      // Show success message
      alert('Quest accepted! Check your Active Quests tab.')
    } catch (err) {
      console.error('Error accepting quest:', err)
      alert('Failed to accept quest. Please try again.')
    }
  }

  // Create a map of quest_id to userQuest for easy lookup
  const userQuestsMap = userQuests.reduce((acc, uq) => {
    acc[uq.quest_id] = uq
    return acc
  }, {})

  // Filter quests based on active tab
  const getFilteredQuests = () => {
    switch (activeTab) {
      case 'available':
        // Show quests that user hasn't accepted yet
        return allQuests.filter(q => !userQuestsMap[q.id])
      case 'active':
        // Show active quests
        return userQuests
          .filter(uq => uq.status === 'active')
          .map(uq => ({ ...uq.quest, userQuest: uq }))
      case 'completed':
        // Show completed quests
        return userQuests
          .filter(uq => uq.status === 'completed')
          .map(uq => ({ ...uq.quest, userQuest: uq }))
      default:
        return []
    }
  }

  const filteredQuests = getFilteredQuests()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading quests...</p>
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
          <h1 className="text-3xl font-bold text-gray-900">Quests & Achievements</h1>
          <p className="text-gray-600 mt-2">Complete challenges, earn rewards, and track your progress</p>
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

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="card bg-gradient-to-br from-blue-50 to-blue-100">
            <div className="text-3xl mb-2">📋</div>
            <div className="text-2xl font-bold text-gray-900">{stats.total_quests}</div>
            <div className="text-sm text-gray-600">Total Quests</div>
          </div>
          <div className="card bg-gradient-to-br from-yellow-50 to-yellow-100">
            <div className="text-3xl mb-2">🎯</div>
            <div className="text-2xl font-bold text-gray-900">{stats.active_quests}</div>
            <div className="text-sm text-gray-600">Active</div>
          </div>
          <div className="card bg-gradient-to-br from-green-50 to-green-100">
            <div className="text-3xl mb-2">✅</div>
            <div className="text-2xl font-bold text-gray-900">{stats.completed_quests}</div>
            <div className="text-sm text-gray-600">Completed</div>
          </div>
          <div className="card bg-gradient-to-br from-purple-50 to-purple-100">
            <div className="text-3xl mb-2">⭐</div>
            <div className="text-2xl font-bold text-gray-900">{stats.total_points_earned}</div>
            <div className="text-sm text-gray-600">Points</div>
          </div>
          <div className="card bg-gradient-to-br from-pink-50 to-pink-100">
            <div className="text-3xl mb-2">🏆</div>
            <div className="text-2xl font-bold text-gray-900">{stats.badges_earned}</div>
            <div className="text-sm text-gray-600">Badges</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          <button
            onClick={() => setActiveTab('available')}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'available'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Available Quests
          </button>
          <button
            onClick={() => setActiveTab('active')}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'active'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Active ({stats?.active_quests || 0})
          </button>
          <button
            onClick={() => setActiveTab('completed')}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'completed'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Completed ({stats?.completed_quests || 0})
          </button>
          <button
            onClick={() => setActiveTab('badges')}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'badges'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            My Badges ({stats?.badges_earned || 0})
          </button>
        </nav>
      </div>

      {/* Content */}
      <div>
        {activeTab === 'badges' ? (
          // Badges Grid
          <div>
            {badges.length === 0 ? (
              <div className="card text-center py-12">
                <div className="text-6xl mb-4">🏆</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No badges yet</h3>
                <p className="text-gray-600">Complete quests to earn your first badge!</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {badges.map((userBadge) => (
                  <BadgeCard key={userBadge.id} userBadge={userBadge} />
                ))}
              </div>
            )}
          </div>
        ) : (
          // Quests Grid
          <div>
            {filteredQuests.length === 0 ? (
              <div className="card text-center py-12">
                <div className="text-6xl mb-4">
                  {activeTab === 'available' && '🎯'}
                  {activeTab === 'active' && '📋'}
                  {activeTab === 'completed' && '✅'}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {activeTab === 'available' && 'All quests accepted!'}
                  {activeTab === 'active' && 'No active quests'}
                  {activeTab === 'completed' && 'No completed quests yet'}
                </h3>
                <p className="text-gray-600">
                  {activeTab === 'available' && 'Check back later for new quests'}
                  {activeTab === 'active' && 'Accept a quest from the Available tab to get started'}
                  {activeTab === 'completed' && 'Complete your first quest to see it here'}
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {filteredQuests.map((quest) => {
                  const userQuest = quest.userQuest || userQuestsMap[quest.id]
                  return (
                    <QuestCard
                      key={quest.id}
                      quest={quest}
                      userQuest={userQuest}
                      onAccept={activeTab === 'available' ? handleAcceptQuest : null}
                    />
                  )
                })}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default QuestsPage
