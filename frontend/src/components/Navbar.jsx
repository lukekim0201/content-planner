import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="max-w-6xl mx-auto px-6 py-3 flex items-center justify-between">
        <Link to={isAuthenticated ? '/dashboard' : '/login'} className="font-semibold text-lg text-gray-900">
          🎬 Content Planner
        </Link>
        {isAuthenticated && (
          <div className="flex items-center gap-4 text-sm">
            {user?.email && <span className="text-gray-500">{user.email}</span>}
            <button onClick={handleLogout} className="text-gray-600 hover:text-gray-900">
              Log out
            </button>
          </div>
        )}
      </div>
    </nav>
  )
}
