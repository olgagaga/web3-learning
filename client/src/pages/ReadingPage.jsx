import { useState, useEffect } from 'react'
import { readingAPI } from '../services/readingAPI'
import ReadingPassage from '../components/reading/ReadingPassage'
import QuestionCard from '../components/reading/QuestionCard'
import ReadingStats from '../components/reading/ReadingStats'
import BadgeNotification from '../components/badges/BadgeNotification'

function ReadingPage() {
  const [readingItem, setReadingItem] = useState(null)
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [feedback, setFeedback] = useState(null)
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedDifficulty, setSelectedDifficulty] = useState(null)
  const [newlyEarnedBadges, setNewlyEarnedBadges] = useState([])

  useEffect(() => {
    loadStats()
    loadNextItem()
  }, [])

  const loadStats = async () => {
    try {
      const response = await readingAPI.getStats()
      setStats(response.data)
    } catch (err) {
      console.error('Failed to load stats:', err)
    }
  }

  const loadNextItem = async (difficulty = null) => {
    setLoading(true)
    setError(null)
    setFeedback(null)
    setCurrentQuestionIndex(0)

    try {
      const response = await readingAPI.getNextItem(difficulty)
      setReadingItem(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load reading item')
    } finally {
      setLoading(false)
    }
  }

  const handleAnswer = async (questionId, userAnswer, timeSpent) => {
    try {
      const response = await readingAPI.submitAnswer(questionId, userAnswer, timeSpent)
      setFeedback(response.data)

      // Check for newly earned badges
      if (response.data.newly_earned_badges && response.data.newly_earned_badges.length > 0) {
        setNewlyEarnedBadges(response.data.newly_earned_badges)
      }

      // Reload stats after submission
      loadStats()
    } catch (err) {
      console.error('Failed to submit answer:', err)
      alert('Failed to submit answer. Please try again.')
    }
  }

  const handleNextQuestion = () => {
    if (currentQuestionIndex < readingItem.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1)
      setFeedback(null)
    } else {
      // All questions answered, load next item
      loadNextItem(selectedDifficulty)
    }
  }

  const handleDifficultyChange = (difficulty) => {
    setSelectedDifficulty(difficulty)
    loadNextItem(difficulty)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Loading reading practice...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Reading Practice</h1>
          <p className="text-gray-600 mt-2">Adaptive reading comprehension exercises</p>
        </div>
        <div className="card bg-red-50 border border-red-200">
          <p className="text-red-700">{error}</p>
          <button onClick={() => loadNextItem()} className="btn-primary mt-4">
            Try Again
          </button>
        </div>
      </div>
    )
  }

  if (!readingItem) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Reading Practice</h1>
          <p className="text-gray-600 mt-2">No reading items available</p>
        </div>
      </div>
    )
  }

  const currentQuestion = readingItem.questions[currentQuestionIndex]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Reading Practice</h1>
          <p className="text-gray-600 mt-2">
            Question {currentQuestionIndex + 1} of {readingItem.questions.length}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">Difficulty:</span>
          <select
            value={selectedDifficulty || ''}
            onChange={(e) => handleDifficultyChange(e.target.value || null)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
          >
            <option value="">Adaptive</option>
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>
        </div>
      </div>

      {stats && <ReadingStats stats={stats} />}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ReadingPassage
          title={readingItem.title}
          passage={readingItem.passage}
          difficulty={readingItem.difficulty}
        />

        <div className="space-y-4">
          <QuestionCard
            question={currentQuestion}
            index={currentQuestionIndex}
            onAnswer={handleAnswer}
            feedback={feedback}
          />

          {feedback && (
            <button onClick={handleNextQuestion} className="btn-primary w-full">
              {currentQuestionIndex < readingItem.questions.length - 1
                ? 'Next Question'
                : 'Load Next Passage'}
            </button>
          )}
        </div>
      </div>

      {/* Badge Notification */}
      <BadgeNotification
        badges={newlyEarnedBadges}
        onClose={() => setNewlyEarnedBadges([])}
      />
    </div>
  )
}

export default ReadingPage
