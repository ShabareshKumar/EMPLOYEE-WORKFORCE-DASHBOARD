import React from 'react'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    // Only log to console — never expose to UI in production
    console.error('Error caught by boundary:', error, errorInfo)
    this.setState({ error, errorInfo })
  }

  handleReload = () => {
    window.location.reload()
  }

  handleGoHome = () => {
    window.location.href = '/dashboard'
  }

  render() {
    if (this.state.hasError) {
      // Determine if we are in development
      // Vite exposes import.meta.env.DEV (not process.env.NODE_ENV)
      const isDev = import.meta.env.DEV

      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
          <div className="card max-w-md w-full">
            <div className="text-center">
              <div className="text-6xl mb-4">⚠️</div>
              <h1 className="text-2xl font-bold text-red-600 mb-4">
                Something went wrong
              </h1>
              <p className="text-gray-600 mb-6">
                We're sorry, but something unexpected happened. Please try
                reloading the page or return to the dashboard.
              </p>

              {/* Dev-only error details — never shown in production */}
              {isDev && this.state.error && (
                <div className="mb-6 p-4 bg-red-50 rounded-lg text-left">
                  <p className="text-sm font-mono text-red-800 mb-2">
                    {String(this.state.error)
                      .replace(/<[^>]*>/g, '')       // strip HTML tags
                      .replace(/[<>&"'`]/g, '')       // strip dangerous chars
                      .substring(0, 200)}
                  </p>
                  {this.state.errorInfo && (
                    <details className="text-xs text-red-700">
                      <summary className="cursor-pointer font-semibold mb-2">
                        Stack trace
                      </summary>
                      <pre className="whitespace-pre-wrap overflow-auto max-h-40">
                        {String(this.state.errorInfo.componentStack)
                          .replace(/<[^>]*>/g, '')
                          .replace(/[<>&"'`]/g, '')
                          .substring(0, 1000)}
                      </pre>
                    </details>
                  )}
                </div>
              )}

              <div className="flex gap-3">
                <button
                  onClick={this.handleReload}
                  className="btn-primary flex-1"
                >
                  Reload Page
                </button>
                <button
                  onClick={this.handleGoHome}
                  className="btn-secondary flex-1"
                >
                  Go to Dashboard
                </button>
              </div>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
