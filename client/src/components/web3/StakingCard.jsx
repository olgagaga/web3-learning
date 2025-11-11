import { useState } from 'react'
import { useAddress } from '@thirdweb-dev/react'

function StakingCard({ onStake }) {
  const address = useAddress()
  const [amount, setAmount] = useState('')
  const [duration, setDuration] = useState('7')
  const [goalType, setGoalType] = useState('streak')
  const [loading, setLoading] = useState(false)

  const handleStake = async () => {
    if (!address) {
      alert('Please connect your wallet first')
      return
    }

    if (!amount || parseFloat(amount) <= 0) {
      alert('Please enter a valid stake amount')
      return
    }

    setLoading(true)
    try {
      await onStake({
        amount,
        duration: parseInt(duration),
        goalType,
      })

      // Reset form
      setAmount('')
      setDuration('7')
      setGoalType('streak')
    } catch (error) {
      console.error('Staking error:', error)
      alert('Failed to create commitment. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
          <span className="text-2xl">🎯</span>
        </div>
        <div>
          <h3 className="text-lg font-bold text-gray-900">Create Commitment</h3>
          <p className="text-sm text-gray-500">Stake tokens to commit to your learning goal</p>
        </div>
      </div>

      <div className="space-y-4">
        {/* Stake Amount */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Stake Amount (ETH)
          </label>
          <input
            type="number"
            step="0.001"
            min="0"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="0.01"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            disabled={loading}
          />
          <p className="text-xs text-gray-500 mt-1">
            Minimum: 0.001 ETH
          </p>
        </div>

        {/* Goal Type */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Goal Type
          </label>
          <select
            value={goalType}
            onChange={(e) => setGoalType(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            disabled={loading}
          >
            <option value="streak">Daily Streak</option>
            <option value="lessons">Complete Lessons</option>
            <option value="score">Achieve Score</option>
            <option value="practice">Practice Hours</option>
          </select>
        </div>

        {/* Duration */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Commitment Duration (days)
          </label>
          <select
            value={duration}
            onChange={(e) => setDuration(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            disabled={loading}
          >
            <option value="7">7 days</option>
            <option value="14">14 days</option>
            <option value="30">30 days</option>
            <option value="90">90 days</option>
          </select>
        </div>

        {/* Stake Button */}
        <button
          onClick={handleStake}
          disabled={!address || loading}
          className={`w-full py-3 rounded-lg font-semibold transition-all ${
            !address || loading
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-primary text-white hover:bg-primary/90 hover:shadow-lg'
          }`}
        >
          {loading ? 'Creating Commitment...' : !address ? 'Connect Wallet First' : 'Create Commitment'}
        </button>

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex gap-2">
            <span className="text-blue-600 text-lg">ℹ️</span>
            <div className="text-sm text-blue-800">
              <p className="font-semibold mb-1">How it works:</p>
              <ul className="list-disc list-inside space-y-1 text-xs">
                <li>Stake tokens to commit to your learning goal</li>
                <li>Complete daily activities to maintain your commitment</li>
                <li>Get your stake back + rewards when you succeed</li>
                <li>Failed commitments go to the scholarship pool</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default StakingCard
