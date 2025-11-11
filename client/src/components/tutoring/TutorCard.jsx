function TutorCard({ tutor, onHire }) {
  const {
    id,
    name,
    bio,
    specializations,
    hourly_rate,
    completed_sessions,
    average_rating,
    reputation_badges,
  } = tutor

  const renderStars = (rating) => {
    const stars = []
    for (let i = 1; i <= 5; i++) {
      stars.push(
        <span key={i} className={i <= rating ? 'text-yellow-500' : 'text-gray-300'}>
          ★
        </span>
      )
    }
    return stars
  }

  return (
    <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200 hover:shadow-lg transition-all">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white text-2xl font-bold">
            {name.charAt(0)}
          </div>
          <div>
            <h3 className="font-bold text-lg text-gray-900">{name}</h3>
            <div className="flex items-center gap-2 text-sm">
              <span className="flex">{renderStars(average_rating)}</span>
              <span className="text-gray-600">({completed_sessions} sessions)</span>
            </div>
          </div>
        </div>

        {/* Badges */}
        <div className="flex items-center gap-1 bg-purple-100 px-3 py-1 rounded-full">
          <span className="text-purple-700 font-semibold text-sm">{reputation_badges}</span>
          <span className="text-xl">🏆</span>
        </div>
      </div>

      {/* Bio */}
      <p className="text-gray-600 text-sm mb-4 line-clamp-3">{bio}</p>

      {/* Specializations */}
      <div className="flex flex-wrap gap-2 mb-4">
        {specializations.map((spec, index) => (
          <span
            key={index}
            className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-xs font-medium"
          >
            {spec}
          </span>
        ))}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-200">
        <div>
          <p className="text-2xl font-bold text-gray-900">{hourly_rate} ETH</p>
          <p className="text-xs text-gray-500">per session</p>
        </div>

        <button
          onClick={() => onHire(tutor)}
          className="px-6 py-2 bg-primary text-white rounded-lg font-semibold hover:bg-primary/90 hover:shadow-lg transition-all"
        >
          Hire Tutor
        </button>
      </div>
    </div>
  )
}

export default TutorCard
