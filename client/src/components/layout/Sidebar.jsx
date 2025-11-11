import { NavLink } from 'react-router-dom'

const navItems = [
  {
    path: '/dashboard',
    icon: '📊',
    label: 'Dashboard',
  },
  {
    path: '/reading',
    icon: '📖',
    label: 'Reading Practice',
  },
  {
    path: '/writing',
    icon: '✍️',
    label: 'Writing Coach',
  },
  {
    path: '/quests',
    icon: '🎯',
    label: 'Quests',
  },
  {
    path: '/badges',
    icon: '🏆',
    label: 'Badges',
  },
  {
    path: '/settings',
    icon: '⚙️',
    label: 'Settings',
  },
]

function Sidebar() {
  return (
    <aside className="w-64 bg-white border-r border-gray-200 min-h-screen flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
            <span className="text-xl">🎓</span>
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-900">EduLearn</h1>
            <p className="text-xs text-gray-500">IELTS/TOEFL Prep</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-1">
          {navItems.map((item) => (
            <li key={item.path}>
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-claude-100 text-primary font-semibold'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`
                }
              >
                <span className="text-xl">{item.icon}</span>
                <span>{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* User section at bottom */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center gap-3 px-4 py-3">
          <div className="w-10 h-10 bg-claude-200 rounded-full flex items-center justify-center">
            <span className="text-lg">👤</span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-gray-900 truncate">User</p>
            <p className="text-xs text-gray-500 truncate">View Profile</p>
          </div>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
