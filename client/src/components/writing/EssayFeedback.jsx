function EssayFeedback({ essay, onRevise }) {
  if (!essay.scores || !essay.feedback) {
    return null
  }

  const { scores, feedback } = essay

  const getScoreColor = (score) => {
    if (score >= 7) return 'text-green-600'
    if (score >= 5.5) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreLabel = (score) => {
    if (score >= 7) return 'Strong'
    if (score >= 5.5) return 'Adequate'
    return 'Needs Improvement'
  }

  return (
    <div className="space-y-6">
      {/* Overall Score */}
      <div className="card bg-gradient-to-br from-claude-50 to-white border border-claude-200">
        <div className="text-center">
          <h3 className="text-sm font-medium text-gray-600 mb-2">Overall Score</h3>
          <div className={`text-5xl font-bold ${getScoreColor(scores.overall_score)}`}>
            {scores.overall_score}
          </div>
          <p className="text-sm text-gray-600 mt-2">{getScoreLabel(scores.overall_score)}</p>
        </div>
      </div>

      {/* Individual Scores */}
      <div className="grid grid-cols-2 gap-4">
        <div className="card">
          <h4 className="text-sm font-medium text-gray-600 mb-1">Task Response</h4>
          <div className={`text-3xl font-bold ${getScoreColor(scores.task_response_score)}`}>
            {scores.task_response_score}
          </div>
        </div>

        <div className="card">
          <h4 className="text-sm font-medium text-gray-600 mb-1">Coherence & Cohesion</h4>
          <div className={`text-3xl font-bold ${getScoreColor(scores.coherence_cohesion_score)}`}>
            {scores.coherence_cohesion_score}
          </div>
        </div>

        <div className="card">
          <h4 className="text-sm font-medium text-gray-600 mb-1">Lexical Resource</h4>
          <div className={`text-3xl font-bold ${getScoreColor(scores.lexical_resource_score)}`}>
            {scores.lexical_resource_score}
          </div>
        </div>

        <div className="card">
          <h4 className="text-sm font-medium text-gray-600 mb-1">Grammatical Range</h4>
          <div className={`text-3xl font-bold ${getScoreColor(scores.grammatical_range_score)}`}>
            {scores.grammatical_range_score}
          </div>
        </div>
      </div>

      {/* Strengths */}
      <div className="card bg-green-50 border border-green-200">
        <h3 className="font-semibold text-green-900 mb-3 flex items-center gap-2">
          <span className="text-xl">✅</span> Strengths
        </h3>
        <ul className="space-y-2">
          {feedback.strengths.map((strength, index) => (
            <li key={index} className="text-sm text-green-800 flex items-start gap-2">
              <span className="text-green-600 mt-0.5">•</span>
              <span>{strength}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Areas for Improvement */}
      <div className="card bg-yellow-50 border border-yellow-200">
        <h3 className="font-semibold text-yellow-900 mb-3 flex items-center gap-2">
          <span className="text-xl">⚠️</span> Areas for Improvement
        </h3>
        <ul className="space-y-2">
          {feedback.weaknesses.map((weakness, index) => (
            <li key={index} className="text-sm text-yellow-800 flex items-start gap-2">
              <span className="text-yellow-600 mt-0.5">•</span>
              <span>{weakness}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Detailed Feedback */}
      <div className="space-y-4">
        <div className="card">
          <h4 className="font-semibold text-gray-900 mb-2">Task Response</h4>
          <p className="text-sm text-gray-700">{feedback.task_response}</p>
        </div>

        <div className="card">
          <h4 className="font-semibold text-gray-900 mb-2">Coherence and Cohesion</h4>
          <p className="text-sm text-gray-700">{feedback.coherence_cohesion}</p>
        </div>

        <div className="card">
          <h4 className="font-semibold text-gray-900 mb-2">Lexical Resource</h4>
          <p className="text-sm text-gray-700">{feedback.lexical_resource}</p>
        </div>

        <div className="card">
          <h4 className="font-semibold text-gray-900 mb-2">Grammatical Range and Accuracy</h4>
          <p className="text-sm text-gray-700">{feedback.grammatical_range}</p>
        </div>
      </div>

      {/* Suggestions */}
      <div className="card bg-blue-50 border border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
          <span className="text-xl">💡</span> Suggestions for Improvement
        </h3>
        <ul className="space-y-2">
          {feedback.suggestions.map((suggestion, index) => (
            <li key={index} className="text-sm text-blue-800 flex items-start gap-2">
              <span className="text-blue-600 mt-0.5">{index + 1}.</span>
              <span>{suggestion}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Revised Outline */}
      <div className="card bg-purple-50 border border-purple-200">
        <h3 className="font-semibold text-purple-900 mb-3 flex items-center gap-2">
          <span className="text-xl">📋</span> Suggested Outline
        </h3>
        <p className="text-sm text-purple-800 whitespace-pre-line">{feedback.revised_outline}</p>
      </div>

      {/* Revise Button */}
      <div className="card bg-gradient-to-br from-primary to-primary-dark text-white">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold mb-1">Ready to improve your essay?</h3>
            <p className="text-sm text-claude-100">
              Revise and resubmit to see your progress
            </p>
          </div>
          <button
            onClick={onRevise}
            className="bg-white text-primary hover:bg-claude-50 font-semibold px-6 py-3 rounded-lg transition-colors"
          >
            Revise Essay
          </button>
        </div>
      </div>
    </div>
  )
}

export default EssayFeedback
