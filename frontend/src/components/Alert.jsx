const Alert = ({ type = 'info', message, onClose }) => {
  const styles = {
    success: 'bg-green-50 border-green-500 text-green-800',
    warning: 'bg-yellow-50 border-yellow-500 text-yellow-800',
    error: 'bg-red-50 border-red-500 text-red-800',
    info: 'bg-blue-50 border-blue-500 text-blue-800'
  }

  const icons = {
    success: '✓',
    warning: '⚠',
    error: '✕',
    info: 'ℹ'
  }

  return (
    <div className={`border-l-4 p-4 rounded-lg ${styles[type]} flex items-center justify-between mb-4 relative z-[60]`}>
      <div className="flex items-center gap-3">
        <span className="text-xl">{icons[type]}</span>
        <p>{message}</p>
      </div>
      
      {onClose && (
        <button onClick={onClose} className="text-xl hover:opacity-70">
          ×
        </button>
      )}
    </div>
  )
}

export default Alert
