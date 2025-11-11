import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { dashboardAPI } from '../services/dashboardAPI'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts'

function DashboardPage() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('overview')
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await dashboardAPI.getStats()
      setStats(response.data)
    } catch (err) {
      console.error('Error loading dashboard:', err)
      setError('Failed to load dashboard data. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (error || !stats) {
    return (
      <div className="card bg-red-50">
        <p className="text-red-600">{error || 'Failed to load data'}</p>
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
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Track your learning progress and achievements</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'overview'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('reading')}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'reading'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Reading Analytics
          </button>
          <button
            onClick={() => setActiveTab('writing')}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'writing'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Writing Analytics
          </button>
          <button
            onClick={() => setActiveTab('quests')}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'quests'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Quests & Progress
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && <OverviewTab stats={stats} navigate={navigate} />}
      {activeTab === 'reading' && <ReadingTab stats={stats} />}
      {activeTab === 'writing' && <WritingTab stats={stats} />}
      {activeTab === 'quests' && <QuestsTab stats={stats} navigate={navigate} />}
    </div>
  )
}

// Overview Tab
function OverviewTab({ stats, navigate }) {
  const { user, overall_progress, streak_info, activity_timeline, recent_achievements } = stats

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card bg-gradient-to-br from-orange-50 to-orange-100">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-orange-200 rounded-lg flex items-center justify-center">
              <span className="text-2xl">🔥</span>
            </div>
            <div>
              <p className="text-sm text-gray-600">Current Streak</p>
              <p className="text-2xl font-bold text-gray-900">{user.current_streak} days</p>
            </div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-green-50 to-green-100">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-green-200 rounded-lg flex items-center justify-center">
              <span className="text-2xl">📖</span>
            </div>
            <div>
              <p className="text-sm text-gray-600">Reading Items</p>
              <p className="text-2xl font-bold text-gray-900">{user.reading_items_completed}</p>
            </div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-blue-50 to-blue-100">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-blue-200 rounded-lg flex items-center justify-center">
              <span className="text-2xl">✍️</span>
            </div>
            <div>
              <p className="text-sm text-gray-600">Essays Written</p>
              <p className="text-2xl font-bold text-gray-900">{user.essays_written}</p>
            </div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-purple-50 to-purple-100">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-purple-200 rounded-lg flex items-center justify-center">
              <span className="text-2xl">🏆</span>
            </div>
            <div>
              <p className="text-sm text-gray-600">Badges Earned</p>
              <p className="text-2xl font-bold text-gray-900">{user.badges_earned}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Level and Progress */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Overall Progress</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-lg font-semibold text-gray-900">
                Level {overall_progress.level.current_level}
              </span>
              <span className="text-sm text-gray-600">
                {overall_progress.level.progress_to_next}% to next level
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-4 mb-6">
              <div
                className="bg-blue-600 h-4 rounded-full transition-all duration-300"
                style={{ width: `${overall_progress.level.progress_to_next}%` }}
              ></div>
            </div>

            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Reading</span>
                  <span className="font-medium">{overall_progress.reading_percentage}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full"
                    style={{ width: `${overall_progress.reading_percentage}%` }}
                  ></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Writing</span>
                  <span className="font-medium">{overall_progress.writing_percentage}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full"
                    style={{ width: `${overall_progress.writing_percentage}%` }}
                  ></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Quests</span>
                  <span className="font-medium">{overall_progress.quest_percentage}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-purple-500 h-2 rounded-full"
                    style={{ width: `${overall_progress.quest_percentage}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Streak Information</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Current Streak:</span>
                <span className="font-semibold text-gray-900">{streak_info.current_streak} days</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Longest Streak:</span>
                <span className="font-semibold text-gray-900">{streak_info.longest_streak} days</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Total Active Days:</span>
                <span className="font-semibold text-gray-900">{streak_info.total_active_days} days</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Activity Timeline */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Activity Timeline (Last 30 Days)</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={activity_timeline}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            />
            <YAxis />
            <Tooltip
              labelFormatter={(date) => new Date(date).toLocaleDateString()}
            />
            <Legend />
            <Line type="monotone" dataKey="reading_items" stroke="#10b981" name="Reading Items" />
            <Line type="monotone" dataKey="essays" stroke="#3b82f6" name="Essays" />
            <Line type="monotone" dataKey="total_activity" stroke="#8b5cf6" name="Total Activity" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Recent Achievements */}
      {recent_achievements && recent_achievements.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Achievements</h2>
          <div className="space-y-3">
            {recent_achievements.map((achievement, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-semibold text-gray-900">{achievement.title}</p>
                  <p className="text-sm text-gray-600">{achievement.description}</p>
                </div>
                <div className="text-right">
                  {achievement.points > 0 && (
                    <span className="text-sm font-semibold text-yellow-600">+{achievement.points} pts</span>
                  )}
                  <p className="text-xs text-gray-500">{new Date(achievement.date).toLocaleDateString()}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => navigate('/reading')}
            className="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all"
          >
            <span className="text-3xl mb-2 block">📖</span>
            <p className="font-semibold text-gray-900">Start Reading Practice</p>
            <p className="text-sm text-gray-600 mt-1">Adaptive exercises</p>
          </button>
          <button
            onClick={() => navigate('/writing')}
            className="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all"
          >
            <span className="text-3xl mb-2 block">✍️</span>
            <p className="font-semibold text-gray-900">Write an Essay</p>
            <p className="text-sm text-gray-600 mt-1">Get AI feedback</p>
          </button>
          <button
            onClick={() => navigate('/quests')}
            className="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all"
          >
            <span className="text-3xl mb-2 block">🎯</span>
            <p className="font-semibold text-gray-900">View Active Quests</p>
            <p className="text-sm text-gray-600 mt-1">Complete challenges</p>
          </button>
        </div>
      </div>
    </div>
  )
}

// Reading Analytics Tab
function ReadingTab({ stats }) {
  const { reading_stats } = stats

  // Prepare skill breakdown data for radar chart
  const skillData = Object.entries(reading_stats.skill_breakdown || {}).map(([skill, data]) => ({
    skill: skill.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    accuracy: data.accuracy,
    total: data.total,
  }))

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <p className="text-sm text-gray-600 mb-1">Total Attempts</p>
          <p className="text-3xl font-bold text-gray-900">{reading_stats.total_attempts}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600 mb-1">Correct Answers</p>
          <p className="text-3xl font-bold text-green-600">{reading_stats.correct_answers}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600 mb-1">Overall Accuracy</p>
          <p className="text-3xl font-bold text-blue-600">{reading_stats.accuracy}%</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600 mb-1">Recommended Level</p>
          <p className="text-2xl font-bold text-gray-900 capitalize">{reading_stats.recommended_difficulty}</p>
        </div>
      </div>

      {/* Skill Breakdown */}
      {skillData.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Skill Performance</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <ResponsiveContainer width="100%" height={300}>
                <RadarChart data={skillData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="skill" />
                  <PolarRadiusAxis angle={90} domain={[0, 100]} />
                  <Radar name="Accuracy" dataKey="accuracy" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </div>
            <div className="space-y-3">
              {skillData.map((skill) => (
                <div key={skill.skill}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-700 font-medium">{skill.skill}</span>
                    <span className="text-gray-600">{skill.accuracy.toFixed(1)}% ({skill.total} items)</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${skill.accuracy}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Writing Analytics Tab
function WritingTab({ stats }) {
  const { writing_stats } = stats

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        <div className="card">
          <p className="text-sm text-gray-600 mb-1">Total Essays</p>
          <p className="text-3xl font-bold text-gray-900">{writing_stats.total_essays}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600 mb-1">Average Score</p>
          <p className="text-3xl font-bold text-blue-600">{writing_stats.average_score}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600 mb-1">Best Score</p>
          <p className="text-3xl font-bold text-green-600">{writing_stats.best_score}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600 mb-1">Revisions</p>
          <p className="text-3xl font-bold text-purple-600">{writing_stats.total_revisions}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600 mb-1">Avg Word Count</p>
          <p className="text-3xl font-bold text-gray-900">{writing_stats.average_word_count}</p>
        </div>
      </div>

      {/* Score Trends */}
      {writing_stats.score_trends && writing_stats.score_trends.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Score Trends</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={writing_stats.score_trends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              />
              <YAxis domain={[0, 9]} />
              <Tooltip
                labelFormatter={(date) => new Date(date).toLocaleDateString()}
              />
              <Legend />
              <Line type="monotone" dataKey="overall_score" stroke="#3b82f6" strokeWidth={2} name="Overall Score" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Skill Averages */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Rubric Scores</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(writing_stats.skill_averages || {}).map(([skill, score]) => (
            <div key={skill}>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-700 font-medium capitalize">{skill.replace(/_/g, ' ')}</span>
                <span className="text-gray-900 font-semibold">{score.toFixed(1)} / 9</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-blue-500 h-3 rounded-full"
                  style={{ width: `${(score / 9) * 100}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Quests Progress Tab
function QuestsTab({ stats, navigate }) {
  const { quest_stats } = stats

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card bg-gradient-to-br from-blue-50 to-blue-100">
          <p className="text-sm text-gray-600 mb-1">Total Quests</p>
          <p className="text-3xl font-bold text-gray-900">{quest_stats.total_quests}</p>
        </div>
        <div className="card bg-gradient-to-br from-yellow-50 to-yellow-100">
          <p className="text-sm text-gray-600 mb-1">Active</p>
          <p className="text-3xl font-bold text-yellow-600">{quest_stats.active_quests}</p>
        </div>
        <div className="card bg-gradient-to-br from-green-50 to-green-100">
          <p className="text-sm text-gray-600 mb-1">Completed</p>
          <p className="text-3xl font-bold text-green-600">{quest_stats.completed_quests}</p>
        </div>
        <div className="card bg-gradient-to-br from-purple-50 to-purple-100">
          <p className="text-sm text-gray-600 mb-1">Points Earned</p>
          <p className="text-3xl font-bold text-purple-600">{quest_stats.total_points_earned}</p>
        </div>
      </div>

      {/* Progress Summary */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quest Progress</h2>
        <div className="space-y-4">
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span className="text-gray-700 font-medium">Completion Rate</span>
              <span className="text-gray-900 font-semibold">
                {quest_stats.total_quests > 0
                  ? Math.round((quest_stats.completed_quests / quest_stats.total_quests) * 100)
                  : 0}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-4">
              <div
                className="bg-green-500 h-4 rounded-full transition-all"
                style={{
                  width: `${
                    quest_stats.total_quests > 0
                      ? (quest_stats.completed_quests / quest_stats.total_quests) * 100
                      : 0
                  }%`,
                }}
              ></div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            <button
              onClick={() => navigate('/quests')}
              className="p-4 border-2 border-blue-200 bg-blue-50 rounded-lg hover:border-blue-500 transition-all"
            >
              <p className="font-semibold text-gray-900">View All Quests</p>
              <p className="text-sm text-gray-600 mt-1">Explore available challenges</p>
            </button>
            <button
              onClick={() => navigate('/badges')}
              className="p-4 border-2 border-purple-200 bg-purple-50 rounded-lg hover:border-purple-500 transition-all"
            >
              <p className="font-semibold text-gray-900">View Badges</p>
              <p className="text-sm text-gray-600 mt-1">{quest_stats.badges_earned} badges earned</p>
            </button>
            <div className="p-4 border-2 border-yellow-200 bg-yellow-50 rounded-lg">
              <p className="font-semibold text-gray-900">Total Points</p>
              <p className="text-2xl font-bold text-yellow-600 mt-1">{quest_stats.total_points_earned}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
