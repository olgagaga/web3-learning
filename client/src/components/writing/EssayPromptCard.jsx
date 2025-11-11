function EssayPromptCard({ prompt, onSelect }) {
  const difficultyColors = {
    easy: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    hard: 'bg-red-100 text-red-800',
  }

  return (
    <div className="card hover:shadow-lg transition-shadow cursor-pointer" onClick={() => onSelect(prompt)}>
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-lg font-semibold text-gray-900">{prompt.title}</h3>
        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${difficultyColors[prompt.difficulty]}`}>
          {prompt.difficulty.charAt(0).toUpperCase() + prompt.difficulty.slice(1)}
        </span>
      </div>

      <p className="text-sm text-gray-600 mb-4 line-clamp-3">
        {prompt.prompt_text}
      </p>

      <div className="flex items-center gap-4 text-sm text-gray-500">
        <span>📝 {prompt.word_count_min}-{prompt.word_count_max} words</span>
        <span>⏱️ {prompt.time_limit_minutes} min</span>
        <span className="capitalize">{prompt.essay_type}</span>
      </div>
    </div>
  )
}

export default EssayPromptCard
