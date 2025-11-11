import { useState, useEffect } from 'react'

function QuestionCard({ question, index, onAnswer, feedback }) {
  const [selectedAnswer, setSelectedAnswer] = useState(null)
  const [startTime] = useState(Date.now())

  useEffect(() => {
    // Reset selection when question changes
    setSelectedAnswer(null)
  }, [question.id])

  const handleAnswerSelect = (option) => {
    if (feedback) return // Don't allow changing answer after submission
    setSelectedAnswer(option)
  }

  const handleSubmit = () => {
    if (!selectedAnswer) return

    const timeSpent = Math.floor((Date.now() - startTime) / 1000)
    onAnswer(question.id, selectedAnswer, timeSpent)
  }

  const getOptionClassName = (option) => {
    const baseClass = 'w-full text-left p-4 rounded-lg border-2 transition-all'

    if (!feedback) {
      // Before submission
      if (selectedAnswer === option) {
        return `${baseClass} border-primary bg-claude-50`
      }
      return `${baseClass} border-gray-200 hover:border-primary hover:bg-gray-50`
    }

    // After submission - show correct/incorrect
    if (option === feedback.correct_answer) {
      return `${baseClass} border-green-500 bg-green-50`
    }
    if (option === selectedAnswer && !feedback.is_correct) {
      return `${baseClass} border-red-500 bg-red-50`
    }
    return `${baseClass} border-gray-200 bg-gray-50 opacity-60`
  }

  return (
    <div className="card">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Question {index + 1}
        </h3>
        <p className="text-gray-700 leading-relaxed">{question.question}</p>
      </div>

      <div className="space-y-3 mb-6">
        {Object.entries(question.options).map(([option, text]) => (
          <button
            key={option}
            onClick={() => handleAnswerSelect(option)}
            disabled={!!feedback}
            className={getOptionClassName(option)}
          >
            <span className="font-semibold text-primary mr-2">{option}.</span>
            <span className="text-gray-700">{text}</span>
          </button>
        ))}
      </div>

      {!feedback && (
        <button
          onClick={handleSubmit}
          disabled={!selectedAnswer}
          className="btn-primary w-full"
        >
          Submit Answer
        </button>
      )}

      {feedback && (
        <div className={`mt-4 p-4 rounded-lg ${feedback.is_correct ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">{feedback.is_correct ? '✅' : '❌'}</span>
            <span className={`font-semibold ${feedback.is_correct ? 'text-green-800' : 'text-red-800'}`}>
              {feedback.is_correct ? 'Correct!' : 'Incorrect'}
            </span>
          </div>
          <p className="text-gray-700 mb-2">
            <strong>Correct Answer:</strong> {feedback.correct_answer}
          </p>
          <p className="text-gray-700">
            <strong>Explanation:</strong> {feedback.explanation}
          </p>
          {feedback.skill_category && (
            <p className="text-sm text-gray-600 mt-2">
              <strong>Skill:</strong> {feedback.skill_category}
            </p>
          )}
        </div>
      )}
    </div>
  )
}

export default QuestionCard
