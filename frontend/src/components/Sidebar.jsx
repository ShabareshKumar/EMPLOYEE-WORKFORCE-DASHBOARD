import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const Sidebar = ({ isOpen, setIsOpen }) => {
  const { user } = useAuth()

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊', roles: ['admin', 'manager', 'employee'] },
    { path: '/timesheets', label: 'Timesheets', icon: '⏱️', roles: ['admin', 'manager', 'employee'] },
    { path: '/analytics', label: 'Analytics', icon: '📈', roles: ['admin', 'manager'] },
    { path: '/projects/upload', label: 'Upload Project', icon: '📁', roles: ['admin', 'manager'] },
    { path: '/admin', label: 'Admin Panel', icon: '⚙️', roles: ['admin'] },
    { path: '/profile', label: 'Profile', icon: '👤', roles: ['admin', 'manager', 'employee'] }
  ]

  // Filter items based on role and demo status
  const filteredItems = navItems.filter(item => {
    // Check role access
    if (!item.roles.includes(user?.role)) return false
    
    // Block demo users from admin panel and upload
    if (user?.is_demo && (item.path === '/admin' || item.path === '/projects/upload')) {
      return false
    }
    
    return true
  })

  return (
    <aside className={`bg-primary text-white transition-all duration-300 ${isOpen ? 'w-64' : 'w-20'}`}>
      <div className="p-6">
        <h1 className={`font-bold text-xl ${!isOpen && 'hidden'}`}>
          Workforce Analytics
        </h1>
        <div className={`text-2xl ${isOpen && 'hidden'}`}>📊</div>
      </div>

      <nav className="mt-6">
        {filteredItems.map(item => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center px-6 py-3 hover:bg-white/10 transition-colors ${
                isActive ? 'bg-white/20 border-r-4 border-pink-500' : ''
              }`
            }
          >
            <span className="text-2xl">{item.icon}</span>
            {isOpen && <span className="ml-4">{item.label}</span>}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}

export default Sidebar
