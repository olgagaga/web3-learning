import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import ReadingPage from './pages/ReadingPage'
import WritingPage from './pages/WritingPage'
import QuestsPage from './pages/QuestsPage'
import BadgesPage from './pages/BadgesPage'
import SettingsPage from './pages/SettingsPage'
import StakingPage from './pages/StakingPage'
import TutoringPage from './pages/TutoringPage'
import ScholarshipPage from './pages/ScholarshipPage'
import MainLayout from './components/layout/MainLayout'

function PrivateRoute({ children }) {
  const { isAuthenticated } = useAuthStore()
  return isAuthenticated ? children : <Navigate to="/login" />
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/*"
          element={
            <PrivateRoute>
              <MainLayout>
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" />} />
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/reading" element={<ReadingPage />} />
                  <Route path="/writing" element={<WritingPage />} />
                  <Route path="/quests" element={<QuestsPage />} />
                  <Route path="/badges" element={<BadgesPage />} />
                  <Route path="/staking" element={<StakingPage />} />
                  <Route path="/tutoring" element={<TutoringPage />} />
                  <Route path="/scholarship" element={<ScholarshipPage />} />
                  <Route path="/settings" element={<SettingsPage />} />
                </Routes>
              </MainLayout>
            </PrivateRoute>
          }
        />
      </Routes>
    </Router>
  )
}

export default App
