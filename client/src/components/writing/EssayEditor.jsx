import { useState, useEffect } from 'react'

function EssayEditor({ prompt, onSubmit, initialContent = '', isRevision = false }) {
  const [content, setContent] = useState(initialContent)
  const [wordCount, setWordCount] = useState(0)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    const words = content.trim().split(/\s+/).filter(word => word.length > 0)
    setWordCount(words.length)
  }, [content])

  const handleSubmit = async () => {
    if (wordCount < prompt.word_count_min) {
      alert(`Please write at least ${prompt.word_count_min} words. Current: ${wordCount}`)
      return
    }

    setSubmitting(true)
    try {
      await onSubmit(content)
    } finally {
      setSubmitting(false)
    }
  }

  const isUnderMin = wordCount < prompt.word_count_min
  const isOverMax = wordCount > prompt.word_count_max

  return (
    <div className="space-y-4">
      <div className="card bg-claude-50 border border-claude-200">
        <h3 className="font-semibold text-gray-900 mb-2">{prompt.title}</h3>
        <p className="text-sm text-gray-700 whitespace-pre-line">{prompt.prompt_text}</p>
        <div className="flex items-center gap-4 mt-3 text-sm text-gray-600">
          <span>📝 {prompt.word_count_min}-{prompt.word_count_max} words</span>
          <span>⏱️ {prompt.time_limit_minutes} minutes</span>
        </div>
      </div>

      <div className="card">
        <div className="flex items-center justify-between mb-3">
          <label className="block text-sm font-medium text-gray-700">
            {isRevision ? 'Revised Essay' : 'Your Essay'}
          </label>
          <div className="flex items-center gap-2">
            <span className={`text-sm font-semibold ${
              isUnderMin ? 'text-red-600' : isOverMax ? 'text-yellow-600' : 'text-green-600'
            }`}>
              {wordCount} words
            </span>
            {isUnderMin && (
              <span className="text-xs text-gray-500">
                (min: {prompt.word_count_min})
              </span>
            )}
            {isOverMax && (
              <span className="text-xs text-gray-500">
                (max: {prompt.word_count_max})
              </span>
            )}
          </div>
        </div>

        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Start writing your essay here..."
          className="w-full h-96 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none resize-none font-serif text-base leading-relaxed"
          disabled={submitting}
        />

        <div className="flex items-center justify-between mt-4">
          <div className="text-sm text-gray-500">
            {isRevision && (
              <span className="text-primary font-semibold">✨ Revision in progress</span>
            )}
          </div>
          <button
            onClick={handleSubmit}
            disabled={submitting || isUnderMin}
            className="btn-primary"
          >
            {submitting ? 'Submitting...' : isRevision ? 'Submit Revision' : 'Submit for Feedback'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default EssayEditor
