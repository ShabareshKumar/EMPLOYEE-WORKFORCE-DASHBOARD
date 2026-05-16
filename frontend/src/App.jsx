import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ErrorBoundary from './components/ErrorBoundary'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Timesheets from './pages/Timesheets'
import Analytics from './pages/Analytics'
import AdminPanel from './pages/AdminPanel'
import Profile from './pages/Profile'
import ProjectUpload from './pages/ProjectUpload'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            
            <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="timesheets" element={<Timesheets />} />
              <Route path="analytics" element={<ProtectedRoute roles={['admin', 'manager']}><Analytics /></ProtectedRoute>} />
              <Route path="admin" element={<ProtectedRoute roles={['admin']}><AdminPanel /></ProtectedRoute>} />
              <Route path="projects/upload" element={<ProtectedRoute roles={['admin', 'manager']}><ProjectUpload /></ProtectedRoute>} />
              <Route path="profile" element={<Profile />} />
            </Route>
          </Routes>
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  )
}

export default App
