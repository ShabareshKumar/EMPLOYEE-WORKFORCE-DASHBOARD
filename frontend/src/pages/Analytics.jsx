import { useEffect, useState } from 'react'
import api from '../api/axios'
import Loader from '../components/Loader'
import StatCard from '../components/StatCard'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js'
import { Bar, Pie, Line } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, PointElement, LineElement, Title, Tooltip, Legend)

const Analytics = () => {
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAnalytics()
  }, [])

  const fetchAnalytics = async () => {
    try {
      const response = await api.get('/analytics')
      setAnalytics(response.data)
    } catch (error) {
      console.error('Error fetching analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <Loader />
  if (!analytics) return <div>No data available</div>

  const { kpis, employee_performance, weekly_trend, insights } = analytics

  // Bar Chart Data - Employee Performance
  const barData = {
    labels: employee_performance.map(emp => emp.name),
    datasets: [{
      label: 'Productivity Score (%)',
      data: employee_performance.map(emp => emp.productivity_score),
      backgroundColor: 'rgba(255, 0, 110, 0.7)',
      borderColor: 'rgba(255, 0, 110, 1)',
      borderWidth: 2,
      borderRadius: 8
    }]
  }

  // Pie Chart Data - Productive vs Non-Productive
  const pieData = {
    labels: ['Productive Hours', 'Non-Productive Hours'],
    datasets: [{
      data: [kpis.productive_hours, kpis.non_productive_hours],
      backgroundColor: ['rgba(34, 197, 94, 0.8)', 'rgba(251, 86, 7, 0.8)'],
      borderWidth: 0
    }]
  }

  // Line Chart Data - Weekly Trend
  const lineData = {
    labels: weekly_trend.map(day => day.date),
    datasets: [{
      label: 'Productivity Score',
      data: weekly_trend.map(day => day.productivity_score),
      borderColor: 'rgba(147, 51, 234, 1)',
      backgroundColor: 'rgba(147, 51, 234, 0.1)',
      tension: 0.4,
      fill: true
    }]
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top'
      }
    }
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Analytics Dashboard</h1>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
        <StatCard
          title="Total Hours"
          value={kpis.total_hours}
          icon="⏰"
          color="blue"
        />
        <StatCard
          title="Productive Hours"
          value={kpis.productive_hours}
          icon="✓"
          color="green"
        />
        <StatCard
          title="Non-Productive"
          value={kpis.non_productive_hours}
          icon="⚠"
          color="orange"
        />
        <StatCard
          title="Productivity"
          value={`${kpis.productivity_percentage}%`}
          icon="📊"
          color="purple"
        />
        <StatCard
          title="Active Employees"
          value={kpis.active_employees}
          icon="👥"
          color="pink"
        />
      </div>

      {/* Insights */}
      {insights && insights.length > 0 && (
        <div className="card mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">🧠 Smart Insights</h2>
          <div className="space-y-3">
            {insights.map((insight, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border-l-4 ${
                  insight.type === 'success' ? 'bg-green-50 border-green-500' :
                  insight.type === 'warning' ? 'bg-yellow-50 border-yellow-500' :
                  'bg-blue-50 border-blue-500'
                }`}
              >
                <p className="font-medium">{insight.message}</p>
                <span className="text-xs text-gray-600 capitalize">
                  Severity: {insight.severity}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Employee Performance</h2>
          <div className="h-80">
            <Bar data={barData} options={chartOptions} />
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Productive vs Non-Productive</h2>
          <div className="h-80 flex items-center justify-center">
            <Pie data={pieData} options={chartOptions} />
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Weekly Productivity Trend</h2>
        <div className="h-80">
          <Line data={lineData} options={chartOptions} />
        </div>
      </div>

      {/* Employee Rankings */}
      <div className="card mt-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Employee Rankings</h2>
        <div className="space-y-3">
          {employee_performance.map((emp, index) => (
            <div key={emp.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-4">
                <span className="text-2xl font-bold text-gray-400">#{index + 1}</span>
                <div>
                  <p className="font-semibold">{emp.name}</p>
                  <p className="text-sm text-gray-600">
                    {emp.total_hours}h total ({emp.productive_hours}h productive)
                  </p>
                </div>
              </div>
              <div className={`px-4 py-2 rounded-full font-bold ${
                emp.productivity_score >= 80 ? 'bg-green-100 text-green-800' :
                emp.productivity_score >= 50 ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {emp.productivity_score}%
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Analytics
