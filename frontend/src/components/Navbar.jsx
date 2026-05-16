import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'

const Navbar = ({ toggleSidebar }) => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <button
          onClick={toggleSidebar}
          className="text-gray-600 hover:text-gray-900"
        >
          ☰
        </button>

        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="font-medium text-gray-900">
              {user?.name}
              {user?.is_demo && (
                <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                  DEMO
                </span>
              )}
            </p>
            <p className="text-sm text-gray-500 capitalize">{user?.role}</p>
          </div>
          
          <button
            onClick={handleLogout}
            className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  )
}

export default Navbar
