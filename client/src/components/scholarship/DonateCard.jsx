import { useState } from 'react'
import { useAddress } from '@thirdweb-dev/react'

function DonateCard({ onDonate }) {
  const address = useAddress()
  const [amount, setAmount] = useState('')
  const [isAnonymous, setIsAnonymous] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleDonate = async () => {
    if (!address) {
      alert('Please connect your wallet first')
      return
    }

    if (!amount || parseFloat(amount) <= 0) {
      alert('Please enter a valid donation amount')
      return
    }

    setLoading(true)
    try {
      await onDonate({ amount: parseFloat(amount), isAnonymous })
      setAmount('')
      setIsAnonymous(false)
    } catch (error) {
      console.error('Donation error:', error)
      alert('Failed to donate. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-md p-6 border border-gray-200">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center text-2xl">
          💰
        </div>
        <div>
          <h3 className="text-lg font-bold text-gray-900">Support Learners</h3>
          <p className="text-sm text-gray-500">Help fund scholarship rewards</p>
        </div>
      </div>

      <div className="space-y-4">
        {/* Amount Input */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Donation Amount (ETH)
          </label>
          <input
            type="number"
            step="0.01"
            min="0.01"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="0.1"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            disabled={loading}
          />
        </div>

        {/* Quick Amounts */}
        <div className="flex gap-2">
          {['0.05', '0.1', '0.25', '0.5'].map((preset) => (
            <button
              key={preset}
              onClick={() => setAmount(preset)}
              className="flex-1 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium"
              disabled={loading}
            >
              {preset} ETH
            </button>
          ))}
        </div>

        {/* Anonymous Option */}
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="anonymous"
            checked={isAnonymous}
            onChange={(e) => setIsAnonymous(e.target.checked)}
            className="w-4 h-4 text-primary focus:ring-primary border-gray-300 rounded"
            disabled={loading}
          />
          <label htmlFor="anonymous" className="text-sm text-gray-700 cursor-pointer">
            Donate anonymously
          </label>
        </div>

        {/* Donate Button */}
        <button
          onClick={handleDonate}
          disabled={!address || loading || !amount}
          className={`w-full py-3 rounded-lg font-semibold transition-all ${
            !address || loading || !amount
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 hover:shadow-lg'
          }`}
        >
          {loading ? 'Processing...' : !address ? 'Connect Wallet First' : 'Donate Now'}
        </button>

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex gap-2 text-sm text-blue-800">
            <span>ℹ️</span>
            <div>
              <p className="font-semibold mb-1">How donations work:</p>
              <ul className="list-disc list-inside space-y-1 text-xs">
                <li>Your donation goes into the scholarship pool</li>
                <li>Matched by platform using quadratic funding</li>
                <li>Distributed to learners with verified improvement</li>
                <li>More donors = larger matching multiplier</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DonateCard
