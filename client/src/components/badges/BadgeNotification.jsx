import { useEffect, useState } from 'react'

function BadgeNotification({ badges, onClose }) {
  const [visible, setVisible] = useState(false)
  const [currentBadgeIndex, setCurrentBadgeIndex] = useState(0)

  useEffect(() => {
    if (badges && badges.length > 0) {
      setVisible(true)
      setCurrentBadgeIndex(0)
    }
  }, [badges])

  if (!badges || badges.length === 0 || !visible) {
    return null
  }

  const currentBadge = badges[currentBadgeIndex]

  const handleNext = () => {
    if (currentBadgeIndex < badges.length - 1) {
      setCurrentBadgeIndex(currentBadgeIndex + 1)
    } else {
      handleClose()
    }
  }

  const handleClose = () => {
    setVisible(false)
    if (onClose) {
      onClose()
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

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
        onClick={handleClose}
      >
        {/* Modal */}
        <div
          className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 relative animate-bounce-in"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Close button */}
          <button
            onClick={handleClose}
            className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          {/* Celebration Header */}
          <div className="text-center mb-6">
            <div className="text-6xl mb-3 animate-pulse">🎉</div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Badge Earned!
            </h2>
            <p className="text-gray-600">
              Congratulations on your achievement!
            </p>
          </div>

          {/* Badge Display */}
          <div className="text-center mb-6">
            {/* Badge Icon */}
            <div className={`w-32 h-32 mx-auto mb-4 rounded-full bg-gradient-to-br ${badgeTypeColors[currentBadge.badge_type]} flex items-center justify-center text-6xl shadow-lg animate-scale-in`}>
              {badgeTypeIcons[currentBadge.badge_type]}
            </div>

            {/* Badge Info */}
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              {currentBadge.name}
            </h3>
            <p className="text-gray-600 mb-4">
              {currentBadge.description}
            </p>

            {/* Badge Type Tag */}
            <span className={`inline-block px-4 py-2 rounded-full text-sm font-semibold capitalize bg-gradient-to-r ${badgeTypeColors[currentBadge.badge_type]} text-white`}>
              {currentBadge.badge_type}
            </span>
          </div>

          {/* Navigation */}
          <div className="flex items-center justify-between pt-4 border-t border-gray-200">
            <div className="text-sm text-gray-500">
              {badges.length > 1 && `${currentBadgeIndex + 1} of ${badges.length}`}
            </div>
            <button
              onClick={handleNext}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              {currentBadgeIndex < badges.length - 1 ? 'Next' : 'Awesome!'}
            </button>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes bounce-in {
          0% {
            transform: scale(0.3);
            opacity: 0;
          }
          50% {
            transform: scale(1.05);
          }
          70% {
            transform: scale(0.9);
          }
          100% {
            transform: scale(1);
            opacity: 1;
          }
        }

        @keyframes scale-in {
          0% {
            transform: scale(0);
            opacity: 0;
          }
          50% {
            transform: scale(1.1);
          }
          100% {
            transform: scale(1);
            opacity: 1;
          }
        }

        .animate-bounce-in {
          animation: bounce-in 0.5s ease-out;
        }

        .animate-scale-in {
          animation: scale-in 0.6s ease-out 0.2s both;
        }
      `}</style>
    </>
  )
}

export default BadgeNotification
