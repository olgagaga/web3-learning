import { useState } from 'react'
import { useAddress } from '@thirdweb-dev/react'
import TutorCard from '../components/tutoring/TutorCard'
import SessionCard from '../components/tutoring/SessionCard'
import HireTutorModal from '../components/tutoring/HireTutorModal'
import ReputationBadges from '../components/tutoring/ReputationBadges'

// Mock data
const MOCK_TUTORS = [
  {
    id: 1,
    name: 'Sarah Chen',
    bio: 'IELTS examiner with 8+ years of experience. Specialized in academic writing and helped 200+ students achieve Band 7+. Patient and detailed feedback guaranteed.',
    specializations: ['IELTS Writing', 'Academic Essays', 'Grammar'],
    hourly_rate: '0.02',
    completed_sessions: 157,
    average_rating: 5,
    reputation_badges: 157,
  },
  {
    id: 2,
    name: 'Michael Torres',
    bio: 'TOEFL speaking coach and accent reduction specialist. Native English speaker from California. Interactive practice sessions with real-time feedback.',
    specializations: ['TOEFL Speaking', 'Pronunciation', 'Accent Training'],
    hourly_rate: '0.025',
    completed_sessions: 89,
    average_rating: 5,
    reputation_badges: 89,
  },
  {
    id: 3,
    name: 'Emma Wilson',
    bio: 'Professional editor and writing coach. PhD in English Literature. Specializing in essay structure, coherence, and advanced vocabulary usage.',
    specializations: ['Essay Structure', 'Vocabulary', 'Editing'],
    hourly_rate: '0.018',
    completed_sessions: 203,
    average_rating: 4,
    reputation_badges: 203,
  },
  {
    id: 4,
    name: 'David Kim',
    bio: 'Reading comprehension expert with a focus on IELTS and TOEFL. Former university lecturer. Clear explanations and proven strategies.',
    specializations: ['Reading Skills', 'Test Strategies', 'Comprehension'],
    hourly_rate: '0.015',
    completed_sessions: 124,
    average_rating: 5,
    reputation_badges: 124,
  },
]

const MOCK_LEARNER_SESSIONS = [
  {
    id: 1,
    title: 'IELTS Task 2 Essay Review',
    description: 'Need feedback on my essay about environmental issues',
    service_type: 'essay_feedback',
    amount: '0.02',
    status: 'pending_review',
    created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    tutor_name: 'Sarah Chen',
    submission_notes: 'Reviewed your essay. Great structure! Added detailed comments on task response and vocabulary.',
  },
  {
    id: 2,
    title: 'TOEFL Speaking Practice - Task 1',
    description: 'Practice for independent speaking task',
    service_type: 'speaking_practice',
    amount: '0.025',
    status: 'in_progress',
    created_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    tutor_name: 'Michael Torres',
  },
]

const MOCK_TUTOR_SESSIONS = [
  {
    id: 3,
    title: 'Academic Writing - University Application',
    description: 'Personal statement review for UK universities',
    service_type: 'writing_coach',
    amount: '0.018',
    status: 'in_progress',
    created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    learner_name: 'John Smith',
  },
  {
    id: 4,
    title: 'Essay Feedback Needed',
    description: null,
    service_type: 'essay_feedback',
    amount: '0.02',
    status: 'created',
    created_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
    learner_name: 'Jane Doe',
  },
]

const MOCK_REPUTATION = {
  total: 157,
  essay_feedback: 98,
  speaking_practice: 32,
  reading_tutor: 15,
  writing_coach: 12,
}

function TutoringPage() {
  const address = useAddress()
  const [activeTab, setActiveTab] = useState('marketplace')
  const [selectedTutor, setSelectedTutor] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [learnerSessions, setLearnerSessions] = useState(MOCK_LEARNER_SESSIONS)
  const [tutorSessions, setTutorSessions] = useState(MOCK_TUTOR_SESSIONS)

  const handleHireTutor = (tutor) => {
    setSelectedTutor(tutor)
    setIsModalOpen(true)
  }

  const handleCreateSession = (sessionData) => {
    console.log('Creating session:', sessionData)

    const newSession = {
      id: learnerSessions.length + 100,
      title: sessionData.title,
      description: sessionData.description,
      service_type: sessionData.service_type,
      amount: sessionData.amount,
      status: 'in_progress',
      created_at: new Date().toISOString(),
      tutor_name: selectedTutor?.name || 'Unknown',
    }

    setLearnerSessions([newSession, ...learnerSessions])
    setIsModalOpen(false)
    setSelectedTutor(null)

    alert('✅ Session created and payment sent to escrow!')
  }

  const handleSessionAction = (action, sessionId) => {
    console.log('Session action:', action, sessionId)

    switch (action) {
      case 'accept':
        setTutorSessions(
          tutorSessions.map((s) =>
            s.id === sessionId ? { ...s, status: 'in_progress' } : s
          )
        )
        alert('✅ Session accepted! You can now start working on it.')
        break

      case 'submit':
        setTutorSessions(
          tutorSessions.map((s) =>
            s.id === sessionId
              ? {
                  ...s,
                  status: 'pending_review',
                  submission_notes: 'Work completed and submitted for review',
                }
              : s
          )
        )
        alert('✅ Work submitted! Waiting for platform verification.')
        break

      case 'review':
        alert('Opening submission review... (Mock)')
        break

      case 'rate':
        alert('Opening rating form... (Mock)')
        break

      case 'cancel':
        setLearnerSessions(
          learnerSessions.map((s) =>
            s.id === sessionId ? { ...s, status: 'cancelled' } : s
          )
        )
        alert('✅ Session cancelled and funds refunded.')
        break

      default:
        break
    }
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Peer Tutoring Marketplace
        </h1>
        <p className="text-gray-600">
          Hire expert tutors with escrow protection and earn reputation badges
        </p>
      </div>

      {/* Connection Warning */}
      {!address && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-8">
          <div className="flex">
            <div className="flex-shrink-0">
              <span className="text-2xl">⚠️</span>
            </div>
            <div className="ml-3">
              <p className="text-sm text-yellow-700">
                <span className="font-semibold">Wallet not connected.</span> Please
                connect your wallet to hire tutors or accept sessions.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 mb-8 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('marketplace')}
          className={`px-6 py-3 font-semibold transition-colors border-b-2 ${
            activeTab === 'marketplace'
              ? 'border-primary text-primary'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          🛒 Marketplace
        </button>
        <button
          onClick={() => setActiveTab('my-sessions')}
          className={`px-6 py-3 font-semibold transition-colors border-b-2 ${
            activeTab === 'my-sessions'
              ? 'border-primary text-primary'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          📝 My Sessions
        </button>
        <button
          onClick={() => setActiveTab('tutor-sessions')}
          className={`px-6 py-3 font-semibold transition-colors border-b-2 ${
            activeTab === 'tutor-sessions'
              ? 'border-primary text-primary'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          🎓 Tutor Dashboard
        </button>
        <button
          onClick={() => setActiveTab('reputation')}
          className={`px-6 py-3 font-semibold transition-colors border-b-2 ${
            activeTab === 'reputation'
              ? 'border-primary text-primary'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          🏆 My Reputation
        </button>
      </div>

      {/* Content */}
      {activeTab === 'marketplace' && (
        <div>
          <div className="mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Available Tutors
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {MOCK_TUTORS.map((tutor) => (
              <TutorCard
                key={tutor.id}
                tutor={tutor}
                onHire={handleHireTutor}
              />
            ))}
          </div>
        </div>
      )}

      {activeTab === 'my-sessions' && (
        <div>
          <div className="mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-2">
              My Learning Sessions
            </h2>
            <p className="text-sm text-gray-600">
              Sessions where you hired a tutor
            </p>
          </div>

          {learnerSessions.length === 0 ? (
            <div className="bg-white rounded-xl shadow-md p-12 text-center border border-gray-200">
              <span className="text-6xl mb-4 block">📭</span>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                No sessions yet
              </h3>
              <p className="text-gray-500 mb-6">
                Hire a tutor from the marketplace to get started!
              </p>
              <button
                onClick={() => setActiveTab('marketplace')}
                className="px-6 py-3 bg-primary text-white rounded-lg font-semibold hover:bg-primary/90"
              >
                Browse Tutors
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-6">
              {learnerSessions.map((session) => (
                <SessionCard
                  key={session.id}
                  session={session}
                  userRole="learner"
                  onAction={handleSessionAction}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'tutor-sessions' && (
        <div>
          <div className="mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-2">
              Tutor Dashboard
            </h2>
            <p className="text-sm text-gray-600">
              Sessions where you are the tutor
            </p>
          </div>

          {tutorSessions.length === 0 ? (
            <div className="bg-white rounded-xl shadow-md p-12 text-center border border-gray-200">
              <span className="text-6xl mb-4 block">🎓</span>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                No tutoring sessions yet
              </h3>
              <p className="text-gray-500">
                Accept open sessions or wait for direct hires
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-6">
              {tutorSessions.map((session) => (
                <SessionCard
                  key={session.id}
                  session={session}
                  userRole="tutor"
                  onAction={handleSessionAction}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'reputation' && (
        <div className="max-w-2xl mx-auto">
          <ReputationBadges badges={MOCK_REPUTATION} />

          <div className="mt-8 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              📜 About Reputation SBTs
            </h3>
            <div className="space-y-3 text-sm text-gray-700">
              <div className="flex gap-3">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
                  1
                </span>
                <p>
                  <strong>Soulbound Tokens (SBTs)</strong> are non-transferable NFTs
                  that represent your achievements
                </p>
              </div>
              <div className="flex gap-3">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
                  2
                </span>
                <p>
                  Earned automatically when you complete tutoring sessions with
                  verified milestones
                </p>
              </div>
              <div className="flex gap-3">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
                  3
                </span>
                <p>
                  Build <strong>portable reputation</strong> that follows you across
                  platforms and employers
                </p>
              </div>
              <div className="flex gap-3">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
                  4
                </span>
                <p>
                  Cannot be bought, sold, or transferred - they represent genuine
                  expertise and work
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Hire Tutor Modal */}
      <HireTutorModal
        tutor={selectedTutor}
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setSelectedTutor(null)
        }}
        onSubmit={handleCreateSession}
      />
    </div>
  )
}

export default TutoringPage
