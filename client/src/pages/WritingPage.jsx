import { useState, useEffect } from 'react'
import { writingAPI } from '../services/writingAPI'
import EssayPromptCard from '../components/writing/EssayPromptCard'
import EssayEditor from '../components/writing/EssayEditor'
import EssayFeedback from '../components/writing/EssayFeedback'
import BadgeNotification from '../components/badges/BadgeNotification'

function WritingPage() {
  const [view, setView] = useState('prompts') // prompts, editor, feedback
  const [prompts, setPrompts] = useState([])
  const [selectedPrompt, setSelectedPrompt] = useState(null)
  const [submittedEssay, setSubmittedEssay] = useState(null)
  const [recentEssays, setRecentEssays] = useState([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [difficultyFilter, setDifficultyFilter] = useState(null)
  const [isRevising, setIsRevising] = useState(false)
  const [newlyEarnedBadges, setNewlyEarnedBadges] = useState([])

  useEffect(() => {
    loadPrompts()
    loadRecentEssays()
  }, [difficultyFilter])

  const loadPrompts = async () => {
    setLoading(true)
    try {
      const response = await writingAPI.getPrompts(difficultyFilter)
      setPrompts(response.data)
    } catch (err) {
      setError('Failed to load prompts')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const loadRecentEssays = async () => {
    try {
      const response = await writingAPI.getEssays(5)
      setRecentEssays(response.data)
    } catch (err) {
      console.error('Failed to load recent essays:', err)
    }
  }

  const handleSelectPrompt = (prompt) => {
    setSelectedPrompt(prompt)
    setIsRevising(false)
    setView('editor')
  }

  const handleSubmitEssay = async (content) => {
    setSubmitting(true)
    setError(null)

    try {
      const parentEssayId = isRevising && submittedEssay ? submittedEssay.id : null
      const response = await writingAPI.submitEssay(
        selectedPrompt.id,
        content,
        parentEssayId
      )

      setSubmittedEssay(response.data)

      // Check for newly earned badges
      if (response.data.newly_earned_badges && response.data.newly_earned_badges.length > 0) {
        setNewlyEarnedBadges(response.data.newly_earned_badges)
      }

      setView('feedback')
      loadRecentEssays()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit essay')
      console.error(err)
    } finally {
      setSubmitting(false)
    }
  }

  const handleRevise = () => {
    setIsRevising(true)
    setView('editor')
  }

  const handleBackToPrompts = () => {
    setView('prompts')
    setSelectedPrompt(null)
    setSubmittedEssay(null)
    setIsRevising(false)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Loading essay prompts...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Writing Coach</h1>
          <p className="text-gray-600 mt-2">
            {view === 'prompts' && 'Choose an essay prompt to begin'}
            {view === 'editor' && (isRevising ? 'Revise your essay' : 'Write your essay')}
            {view === 'feedback' && 'AI Feedback and Suggestions'}
          </p>
        </div>

        {view !== 'prompts' && (
          <button onClick={handleBackToPrompts} className="btn-secondary">
            ← Back to Prompts
          </button>
        )}
      </div>

      {error && (
        <div className="card bg-red-50 border border-red-200">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Prompts View */}
      {view === 'prompts' && (
        <>
          {/* Difficulty Filter */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">Filter by difficulty:</span>
            <select
              value={difficultyFilter || ''}
              onChange={(e) => setDifficultyFilter(e.target.value || null)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            >
              <option value="">All Levels</option>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>

          {/* Recent Essays */}
          {recentEssays.length > 0 && (
            <div className="card bg-claude-50 border border-claude-200">
              <h3 className="font-semibold text-gray-900 mb-3">Recent Essays</h3>
              <div className="space-y-2">
                {recentEssays.map((essay) => (
                  <div
                    key={essay.id}
                    className="flex items-center justify-between p-3 bg-white rounded-lg"
                  >
                    <div>
                      <p className="font-medium text-gray-900">{essay.prompt_title}</p>
                      <p className="text-sm text-gray-500">
                        {essay.word_count} words • {new Date(essay.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    {essay.overall_score && (
                      <div className="text-2xl font-bold text-primary">
                        {essay.overall_score}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Essay Prompts */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {prompts.map((prompt) => (
              <EssayPromptCard
                key={prompt.id}
                prompt={prompt}
                onSelect={handleSelectPrompt}
              />
            ))}
          </div>

          {prompts.length === 0 && (
            <div className="card text-center text-gray-600">
              <p>No essay prompts available for the selected difficulty level.</p>
            </div>
          )}
        </>
      )}

      {/* Editor View */}
      {view === 'editor' && selectedPrompt && (
        <EssayEditor
          prompt={selectedPrompt}
          onSubmit={handleSubmitEssay}
          initialContent={isRevising && submittedEssay ? submittedEssay.content : ''}
          isRevision={isRevising}
        />
      )}

      {/* Feedback View */}
      {view === 'feedback' && submittedEssay && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Essay Content */}
          <div className="lg:col-span-1">
            <div className="card sticky top-6">
              <h3 className="font-semibold text-gray-900 mb-3">Your Essay</h3>
              <div className="max-h-96 overflow-y-auto">
                <p className="text-sm text-gray-700 whitespace-pre-line leading-relaxed">
                  {submittedEssay.content}
                </p>
              </div>
              <div className="mt-4 pt-4 border-t border-gray-200">
                <p className="text-sm text-gray-600">
                  Word Count: <span className="font-semibold">{submittedEssay.word_count}</span>
                </p>
                {submittedEssay.submission_number > 1 && (
                  <p className="text-sm text-primary font-semibold mt-1">
                    Revision #{submittedEssay.submission_number}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Feedback */}
          <div className="lg:col-span-2">
            <EssayFeedback essay={submittedEssay} onRevise={handleRevise} />
          </div>
        </div>
      )}

      {/* Badge Notification */}
      <BadgeNotification
        badges={newlyEarnedBadges}
        onClose={() => setNewlyEarnedBadges([])}
      />
    </div>
  )
}

export default WritingPage
