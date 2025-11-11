function LeaderboardTable({ data, title, type = 'improvers' }) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-md p-12 text-center border border-gray-200">
        <span className="text-6xl mb-4 block">📊</span>
        <p className="text-gray-500">No data available yet</p>
      </div>
    )
  }

  const getMedalIcon = (index) => {
    switch (index) {
      case 0:
        return '🥇'
      case 1:
        return '🥈'
      case 2:
        return '🥉'
      default:
        return `${index + 1}`
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-6">
        <h3 className="text-xl font-bold">{title}</h3>
        <p className="text-purple-100 text-sm mt-1">Community achievements</p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Rank
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                {type === 'improvers' ? 'Learner' : 'Donor'}
              </th>
              <th className="px-6 py-3 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">
                {type === 'improvers' ? 'Improvement' : 'Donated'}
              </th>
              <th className="px-6 py-3 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">
                {type === 'improvers' ? 'Reward' : 'Impact'}
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {data.map((item, index) => (
              <tr
                key={index}
                className={`hover:bg-gray-50 transition-colors ${
                  index < 3 ? 'bg-yellow-50/30' : ''
                }`}
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <span className="text-2xl">{getMedalIcon(index)}</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold">
                      {item.name.charAt(0)}
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">{item.name}</p>
                      {type === 'improvers' && (
                        <p className="text-xs text-gray-500">{item.metric_type}</p>
                      )}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  {type === 'improvers' ? (
                    <span className="text-lg font-bold text-green-600">
                      +{item.improvement_percent}%
                    </span>
                  ) : (
                    <span className="text-lg font-bold text-blue-600">
                      {item.amount} ETH
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  {type === 'improvers' ? (
                    <span className="font-semibold text-gray-900">{item.reward} ETH</span>
                  ) : (
                    <div className="text-right">
                      <p className="font-semibold text-gray-900">{item.learners_supported}</p>
                      <p className="text-xs text-gray-500">learners</p>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default LeaderboardTable
