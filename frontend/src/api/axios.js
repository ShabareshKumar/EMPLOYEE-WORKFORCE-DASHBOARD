import axios from 'axios'

// In production VITE_API_URL must be set — fail fast if missing
if (import.meta.env.PROD && !import.meta.env.VITE_API_URL) {
  throw new Error(
    '[CONFIG ERROR] VITE_API_URL is not set. ' +
    'Add it to Vercel environment variables: VITE_API_URL=https://your-backend.onrender.com/api'
  )
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_URL,
  timeout: 60000, // 60s — handles Render free tier cold start (can take 30-60s)
  headers: {
    'Content-Type': 'application/json'
  }
})

// Attach JWT token to every request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Handle 401 globally — clear auth and redirect to login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
