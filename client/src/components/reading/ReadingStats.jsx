function ReadingStats({ stats }) {
  if (!stats) return null

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div className="card">
        <div className="text-sm text-gray-600 mb-1">Total Attempts</div>
        <div className="text-3xl font-bold text-gray-900">{stats.total_attempts}</div>
      </div>

      <div className="card">
        <div className="text-sm text-gray-600 mb-1">Accuracy</div>
        <div className="text-3xl font-bold text-primary">{stats.accuracy}%</div>
      </div>

      <div className="card">
        <div className="text-sm text-gray-600 mb-1">Recommended Level</div>
        <div className="text-2xl font-bold text-gray-900 capitalize">
          {stats.recommended_difficulty}
        </div>
      </div>
    </div>
  )
}

export default ReadingStats
