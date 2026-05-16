import { useEffect, useState } from 'react'
import api from '../api/axios'
import Loader from '../components/Loader'
import Alert from '../components/Alert'
import Modal from '../components/Modal'
import ProjectSelector from '../components/ProjectSelector'

const Timesheets = () => {
  const [timesheets, setTimesheets] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [alert, setAlert] = useState(null)
  const [useStructuredFormat, setUseStructuredFormat] = useState(false)
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    project: '',
    task: '',
    project_id: null,
    category_id: null,
    task_id: null,
    productive_hours: '',
    non_productive_hours: '',
    description: ''
  })

  useEffect(() => {
    fetchTimesheets()
  }, [])

  const fetchTimesheets = async () => {
    try {
      const response = await api.get('/timesheets')
      setTimesheets(response.data.timesheets)
    } catch (error) {
      showAlert('error', 'Failed to fetch timesheets')
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
      // Prepare data based on format
      const submitData = { ...formData }
      
      // If using structured format, remove legacy fields
      if (useStructuredFormat && formData.project_id) {
        delete submitData.project
        delete submitData.task
      } else {
        // If using legacy format, remove structured fields
        delete submitData.project_id
        delete submitData.category_id
        delete submitData.task_id
      }
      
      if (editingId) {
        await api.put(`/timesheets/${editingId}`, submitData)
        showAlert('success', 'Timesheet updated successfully')
      } else {
        await api.post('/timesheets', submitData)
        showAlert('success', 'Timesheet created successfully')
      }
      
      setShowModal(false)
      resetForm()
      fetchTimesheets()
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Operation failed'
      showAlert('error', errorMessage)
    }
  }

  const handleProjectSelection = (selection) => {
    setFormData({
      ...formData,
      project_id: selection.projectId,
      category_id: selection.categoryId,
      task_id: selection.taskId
    })
  }

  const handleEdit = (timesheet) => {
    setEditingId(timesheet.id)
    setFormData({
      date: timesheet.date,
      project: timesheet.project,
      task: timesheet.task,
      productive_hours: timesheet.productive_hours,
      non_productive_hours: timesheet.non_productive_hours,
      description: timesheet.description || ''
    })
    setShowModal(true)
  }

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this entry?')) return
    
    try {
      await api.delete(`/timesheets/${id}`)
      showAlert('success', 'Timesheet deleted successfully')
      fetchTimesheets()
    } catch (error) {
      showAlert('error', 'Failed to delete timesheet')
    }
  }

  const resetForm = () => {
    setFormData({
      date: new Date().toISOString().split('T')[0],
      project: '',
      task: '',
      project_id: null,
      category_id: null,
      task_id: null,
      productive_hours: '',
      non_productive_hours: '',
      description: ''
    })
    setEditingId(null)
    setUseStructuredFormat(false)
  }

  if (loading) return <Loader />

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Timesheets</h1>
        <button
          onClick={() => {
            resetForm()
            setShowModal(true)
          }}
          className="btn-primary"
        >
          + Add Entry
        </button>
      </div>

      {alert && <Alert type={alert.type} message={alert.message} onClose={() => setAlert(null)} />}

      <div className="card overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-3 px-4">Date</th>
              <th className="text-left py-3 px-4">Project</th>
              <th className="text-left py-3 px-4">Task</th>
              <th className="text-left py-3 px-4">Productive</th>
              <th className="text-left py-3 px-4">Non-Productive</th>
              <th className="text-left py-3 px-4">Total</th>
              <th className="text-left py-3 px-4">Score</th>
              <th className="text-left py-3 px-4">Actions</th>
            </tr>
          </thead>
          <tbody>
            {timesheets.map(timesheet => (
              <tr key={timesheet.id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="py-3 px-4">{timesheet.date}</td>
                <td className="py-3 px-4">{timesheet.project}</td>
                <td className="py-3 px-4">{timesheet.task}</td>
                <td className="py-3 px-4">{timesheet.productive_hours}h</td>
                <td className="py-3 px-4">{timesheet.non_productive_hours}h</td>
                <td className="py-3 px-4 font-semibold">{timesheet.total_hours}h</td>
                <td className="py-3 px-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                    timesheet.productivity_score >= 80 ? 'bg-green-100 text-green-800' :
                    timesheet.productivity_score >= 50 ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {timesheet.productivity_score}%
                  </span>
                </td>
                <td className="py-3 px-4">
                  <button
                    onClick={() => handleEdit(timesheet)}
                    className="text-blue-600 hover:text-blue-800 mr-3"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(timesheet.id)}
                    className="text-red-600 hover:text-red-800"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {timesheets.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            No timesheets found. Add your first entry!
          </div>
        )}
      </div>

      {showModal && (
        <Modal onClose={() => { setShowModal(false); resetForm(); }}>
          <h2 className="text-2xl font-bold mb-4">
            {editingId ? 'Edit Timesheet' : 'Add Timesheet'}
          </h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Date</label>
              <input
                type="date"
                value={formData.date}
                onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                className="input-field"
                required
              />
            </div>

            <div className="mb-4">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={useStructuredFormat}
                  onChange={(e) => setUseStructuredFormat(e.target.checked)}
                  className="w-4 h-4 text-blue-600"
                />
                <span className="text-sm font-medium">Use Project Template (Structured)</span>
              </label>
              <p className="text-xs text-gray-500 mt-1">
                {useStructuredFormat 
                  ? 'Select from uploaded project templates' 
                  : 'Enter project and task manually'}
              </p>
            </div>

            {useStructuredFormat ? (
              <ProjectSelector
                onSelect={handleProjectSelection}
                selectedValues={{
                  projectId: formData.project_id,
                  categoryId: formData.category_id,
                  taskId: formData.task_id
                }}
              />
            ) : (
              <>
                <div>
                  <label className="block text-sm font-medium mb-2">Project</label>
                  <input
                    type="text"
                    value={formData.project}
                    onChange={(e) => setFormData({ ...formData, project: e.target.value })}
                    className="input-field"
                    placeholder="Project name"
                    required={!useStructuredFormat}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Task</label>
                  <input
                    type="text"
                    value={formData.task}
                    onChange={(e) => setFormData({ ...formData, task: e.target.value })}
                    className="input-field"
                    placeholder="Task description"
                    required={!useStructuredFormat}
                  />
                </div>
              </>
            )}

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Productive Hours</label>
                <input
                  type="number"
                  step="0.5"
                  min="0"
                  max="24"
                  value={formData.productive_hours}
                  onChange={(e) => setFormData({ ...formData, productive_hours: e.target.value })}
                  className="input-field"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Non-Productive Hours</label>
                <input
                  type="number"
                  step="0.5"
                  min="0"
                  max="24"
                  value={formData.non_productive_hours}
                  onChange={(e) => setFormData({ ...formData, non_productive_hours: e.target.value })}
                  className="input-field"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Description (Optional)</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="input-field"
                rows="3"
                placeholder="Additional notes..."
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

export default Timesheets
