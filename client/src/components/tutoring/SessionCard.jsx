function SessionCard({ session, userRole, onAction }) {
  const {
    id,
    title,
    description,
    service_type,
    amount,
    status,
    created_at,
    tutor_name,
    learner_name,
    submission_notes,
  } = session

  const getStatusColor = () => {
    switch (status) {
      case 'created':
        return 'bg-yellow-100 text-yellow-800'
      case 'in_progress':
        return 'bg-blue-100 text-blue-800'
      case 'pending_review':
        return 'bg-purple-100 text-purple-800'
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'disputed':
        return 'bg-red-100 text-red-800'
      case 'cancelled':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getServiceIcon = () => {
    switch (service_type) {
      case 'essay_feedback':
        return '📝'
      case 'speaking_practice':
        return '🗣️'
      case 'reading_tutor':
        return '📖'
      case 'writing_coach':
        return '✍️'
      default:
        return '🎓'
    }
  }

  const getServiceLabel = () => {
    switch (service_type) {
      case 'essay_feedback':
        return 'Essay Feedback'
      case 'speaking_practice':
        return 'Speaking Practice'
      case 'reading_tutor':
        return 'Reading Tutor'
      case 'writing_coach':
        return 'Writing Coach'
      default:
        return service_type
    }
  }

  const renderActionButtons = () => {
    if (userRole === 'tutor') {
      if (status === 'created') {
        return (
          <button
            onClick={() => onAction('accept', id)}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
          >
            Accept Session
          </button>
        )
      }
      if (status === 'in_progress') {
        return (
          <button
            onClick={() => onAction('submit', id)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Submit Work
          </button>
        )
      }
    }

    if (userRole === 'learner') {
      if (status === 'created') {
        return (
          <button
            onClick={() => onAction('cancel', id)}
            className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors font-medium"
          >
            Cancel
          </button>
        )
      }
      if (status === 'pending_review') {
        return (
          <button
            onClick={() => onAction('review', id)}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium"
          >
            Review Submission
          </button>
        )
      }
      if (status === 'completed') {
        return (
          <button
            onClick={() => onAction('rate', id)}
            className="px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 transition-colors font-medium"
          >
            Rate Tutor
          </button>
        )
      }
    }

    return null
  }

  return (
    <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200 hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-2xl">
            {getServiceIcon()}
          </div>
          <div>
            <h3 className="font-bold text-lg text-gray-900">{title}</h3>
            <p className="text-sm text-gray-500">{getServiceLabel()}</p>
          </div>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor()}`}>
          {status.replace('_', ' ').toUpperCase()}
        </span>
      </div>

      {/* Description */}
      {description && (
        <p className="text-gray-600 text-sm mb-4 line-clamp-2">{description}</p>
      )}

      {/* Submission Notes (if available) */}
      {submission_notes && status === 'pending_review' && (
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-3 mb-4">
          <p className="text-sm text-purple-900">
            <span className="font-semibold">Submission:</span> {submission_notes}
          </p>
        </div>
      )}

      {/* Participants */}
      <div className="flex items-center justify-between text-sm mb-4 pb-4 border-b border-gray-200">
        <div>
          <p className="text-gray-500">
            {userRole === 'tutor' ? 'Learner' : 'Tutor'}:
          </p>
          <p className="font-semibold text-gray-900">
            {userRole === 'tutor' ? learner_name : tutor_name || 'Not assigned'}
          </p>
        </div>
        <div className="text-right">
          <p className="text-gray-500">Amount:</p>
          <p className="font-bold text-xl text-gray-900">{amount} ETH</p>
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between">
        <p className="text-xs text-gray-500">
          Created {new Date(created_at).toLocaleDateString()}
        </p>
        {renderActionButtons()}
      </div>
    </div>
  )
}

export default SessionCard
