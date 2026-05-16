import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../api/axios'
import StatCard from '../components/StatCard'
import Loader from '../components/Loader'

const Dashboard = () => {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/timesheets')
      const timesheets = response.data.timesheets

      const totalHours = timesheets.reduce((sum, t) => sum + t.total_hours, 0)
      const productiveHours = timesheets.reduce((sum, t) => sum + t.productive_hours, 0)
      const productivity = totalHours > 0 ? ((productiveHours / totalHours) * 100).toFixed(1) : 0

      setStats({
        totalHours: totalHours.toFixed(1),
        productiveHours: productiveHours.toFixed(1),
        productivity: productivity,
        entries: timesheets.length
      })
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <Loader />

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.name}! 👋
        </h1>
        <p className="text-gray-600 mt-2">Here's your productivity overview</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Hours"
          value={stats?.totalHours || 0}
          icon="⏰"
          color="blue"
        />
        <StatCard
          title="Productive Hours"
          value={stats?.productiveHours || 0}
          icon="✓"
          color="green"
        />
        <StatCard
          title="Productivity Score"
          value={`${stats?.productivity || 0}%`}
          icon="📊"
          color="purple"
        />
        <StatCard
          title="Total Entries"
          value={stats?.entries || 0}
          icon="📝"
          color="orange"
        />
      </div>

      <div className="mt-8 card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <a href="/timesheets" className="p-4 border-2 border-gray-200 rounded-xl hover:border-pink-500 transition-colors">
            <div className="text-3xl mb-2">⏱️</div>
            <h3 className="font-semibold">Log Time</h3>
            <p className="text-sm text-gray-600">Add new timesheet entry</p>
          </a>
          
          {['admin', 'manager'].includes(user?.role) && (
            <a href="/analytics" className="p-4 border-2 border-gray-200 rounded-xl hover:border-pink-500 transition-colors">
              <div className="text-3xl mb-2">📈</div>
              <h3 className="font-semibold">View Analytics</h3>
              <p className="text-sm text-gray-600">Team productivity insights</p>
            </a>
          )}
          
          <a href="/profile" className="p-4 border-2 border-gray-200 rounded-xl hover:border-pink-500 transition-colors">
            <div className="text-3xl mb-2">👤</div>
            <h3 className="font-semibold">Profile</h3>
            <p className="text-sm text-gray-600">Manage your account</p>
          </a>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
