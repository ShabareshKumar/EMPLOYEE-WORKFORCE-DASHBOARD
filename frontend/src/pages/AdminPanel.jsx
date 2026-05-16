import { useEffect, useState } from 'react'
import api from '../api/axios'
import Loader from '../components/Loader'
import Alert from '../components/Alert'
import Modal from '../components/Modal'

const AdminPanel = () => {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [alert, setAlert] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    role: 'employee',
    department: ''
  })

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      const response = await api.get('/users')
      setUsers(response.data.users)
    } catch (error) {
      showAlert('error', 'Failed to fetch users')
    } finally {
      setLoading(false)
    }
  }

  const showAlert = (type, message) => {
    setAlert({ type, message })
    setTimeout(() => setAlert(null), 5000)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    try {
      if (editingId) {
        // Don't send password if it's empty (keep existing password)
        const updateData = { ...formData }
        if (!updateData.password) {
          delete updateData.password
        }
        await api.put(`/users/${editingId}`, updateData)
        showAlert('success', 'User updated successfully')
      } else {
        await api.post('/users', formData)
        showAlert('success', 'User created successfully')
      }
      
      setShowModal(false)
      resetForm()
      fetchUsers()
    } catch (error) {
      showAlert('error', error.response?.data?.message || 'Operation failed')
    }
  }

  const handleEdit = (user) => {
    setEditingId(user.id)
    setFormData({
      name: user.name,
      email: user.email,
      password: '',
      role: user.role,
      department: user.department || ''
    })
    setShowModal(true)
  }

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this user?')) return
    
    try {
      await api.delete(`/users/${id}`)
      showAlert('success', 'User deleted successfully')
      fetchUsers()
    } catch (error) {
      showAlert('error', error.response?.data?.message || 'Failed to delete user')
    }
  }

  const resetForm = () => {
    setFormData({
      name: '',
      email: '',
      password: '',
      role: 'employee',
      department: ''
    })
    setEditingId(null)
  }

  if (loading) return <Loader />

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Admin Panel</h1>
        <button
          onClick={() => {
            resetForm()
            setShowModal(true)
          }}
          className="btn-primary"
        >
          + Add User
        </button>
      </div>

      {alert && <Alert type={alert.type} message={alert.message} onClose={() => setAlert(null)} />}

      <div className="card overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-3 px-4">Name</th>
              <th className="text-left py-3 px-4">Email</th>
              <th className="text-left py-3 px-4">Role</th>
              <th className="text-left py-3 px-4">Department</th>
              <th className="text-left py-3 px-4">Created</th>
              <th className="text-left py-3 px-4">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="py-3 px-4 font-medium">{user.name}</td>
                <td className="py-3 px-4">{user.email}</td>
                <td className="py-3 px-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    user.role === 'admin' ? 'bg-purple-100 text-purple-800' :
                    user.role === 'manager' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {user.role}
                  </span>
                </td>
                <td className="py-3 px-4">{user.department || '-'}</td>
                <td className="py-3 px-4">{new Date(user.created_at).toLocaleDateString()}</td>
                <td className="py-3 px-4">
                  <button
                    onClick={() => handleEdit(user)}
                    className="text-blue-600 hover:text-blue-800 mr-3"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(user.id)}
                    className="text-red-600 hover:text-red-800"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <Modal onClose={() => { setShowModal(false); resetForm(); }}>
          <h2 className="text-2xl font-bold mb-4">
            {editingId ? 'Edit User' : 'Add User'}
          </h2>
          
          {alert && <Alert type={alert.type} message={alert.message} onClose={() => setAlert(null)} />}
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="input-field"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="input-field"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Password {editingId && '(leave blank to keep current)'}
              </label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="input-field"
                required={!editingId}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Role</label>
              <select
                value={formData.role}
                onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                className="input-field"
                required
              >
                <option value="employee">Employee</option>
                <option value="manager">Manager</option>
                <option value="admin">Admin</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Department</label>
              <input
                type="text"
                value={formData.department}
                onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                className="input-field"
                placeholder="e.g., Engineering, Sales"
              />
            </div>

            <div className="flex gap-3">
              <button type="submit" className="btn-primary flex-1">
                {editingId ? 'Update' : 'Create'}
              </button>
              <button
                type="button"
                onClick={() => { setShowModal(false); resetForm(); }}
                className="btn-secondary flex-1"
              >
                Cancel
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}

export default AdminPanel
