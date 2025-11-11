import { useState } from 'react'

function HireTutorModal({ tutor, isOpen, onClose, onSubmit }) {
  const [formData, setFormData] = useState({
    service_type: 'essay_feedback',
    title: '',
    description: '',
    amount: tutor?.hourly_rate || '0.01',
  })

  if (!isOpen || !tutor) return null

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit({ ...formData, tutor_id: tutor.id })
    setFormData({
      service_type: 'essay_feedback',
      title: '',
      description: '',
      amount: tutor.hourly_rate,
    })
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center text-2xl font-bold">
                {tutor.name.charAt(0)}
              </div>
              <div>
                <h2 className="text-2xl font-bold">Hire {tutor.name}</h2>
                <p className="text-blue-100 text-sm">{tutor.hourly_rate} ETH per session</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:bg-white/20 rounded-full w-10 h-10 flex items-center justify-center transition-colors"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Service Type */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Service Type
            </label>
            <select
              name="service_type"
              value={formData.service_type}
              onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              required
            >
              <option value="essay_feedback">📝 Essay Feedback</option>
              <option value="speaking_practice">🗣️ Speaking Practice</option>
              <option value="reading_tutor">📖 Reading Tutor</option>
              <option value="writing_coach">✍️ Writing Coach</option>
            </select>
          </div>

          {/* Title */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Session Title
            </label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              placeholder="e.g., IELTS Task 2 Essay Review"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              required
              minLength={10}
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Description (Optional)
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Provide details about what you need help with..."
              rows={4}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
            />
          </div>

          {/* Amount */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Payment Amount (ETH)
            </label>
            <input
              type="number"
              name="amount"
              value={formData.amount}
              onChange={handleChange}
              step="0.001"
              min="0.001"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              5% platform fee will be deducted
            </p>
          </div>

          {/* Info Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex gap-3">
              <span className="text-blue-600 text-2xl">ℹ️</span>
              <div className="text-sm text-blue-800">
                <p className="font-semibold mb-2">How escrow works:</p>
                <ul className="list-disc list-inside space-y-1 text-xs">
                  <li>Payment is held in escrow until work is verified</li>
                  <li>Tutor submits work when complete</li>
                  <li>Platform verifies milestone completion</li>
                  <li>Funds are released to tutor automatically</li>
                  <li>Tutor receives a reputation SBT upon completion</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Buttons */}
          <div className="flex gap-4 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-6 py-3 bg-primary text-white rounded-lg font-semibold hover:bg-primary/90 hover:shadow-lg transition-all"
            >
              Create Session & Pay {formData.amount} ETH
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default HireTutorModal
