import { useState } from 'react';
import api from '../api/axios';
import Alert from '../components/Alert';
import Loader from '../components/Loader';

export default function ProjectUpload() {
  const [file, setFile] = useState(null);
  const [projectName, setProjectName] = useState('');
  const [projectDescription, setProjectDescription] = useState('');
  const [privacyMode, setPrivacyMode] = useState('strict');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      const ext = selectedFile.name.split('.').pop().toLowerCase();
      if (['xlsx', 'xls', 'csv'].includes(ext)) {
        setFile(selectedFile);
        setAlert(null);
      } else {
        setAlert({ type: 'error', message: 'Please select an Excel (.xlsx, .xls) or CSV file' });
        setFile(null);
      }
    }
  };

  const handleAnalyze = async () => {
    if (!file) {
      setAlert({ type: 'error', message: 'Please select a file first' });
      return;
    }

    setLoading(true);
    setAnalysis(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('privacy_mode', privacyMode);

      const response = await api.post('/projects/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setAnalysis(response.data);
      setAlert({ type: 'success', message: 'File analyzed successfully!' });
    } catch (error) {
      setAlert({
        type: 'error',
        message: error.response?.data?.message || 'Failed to analyze file'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async () => {
    if (!file || !projectName.trim()) {
      setAlert({ type: 'error', message: 'Please provide file and project name' });
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('project_name', projectName);
      formData.append('project_description', projectDescription);
      formData.append('privacy_mode', privacyMode);

      const response = await api.post('/projects/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setAlert({ type: 'success', message: 'Project created successfully!' });
      
      // Reset form
      setFile(null);
      setProjectName('');
      setProjectDescription('');
      setAnalysis(null);
      
      // Show project details
      console.log('Created project:', response.data.project);
    } catch (error) {
      setAlert({
        type: 'error',
        message: error.response?.data?.message || 'Failed to create project'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Upload Project Template</h1>

      {alert && (
        <Alert
          type={alert.type}
          message={alert.message}
          onClose={() => setAlert(null)}
        />
      )}

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Step 1: Select Excel File</h2>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Excel File (.xlsx, .xls, .csv)
          </label>
          <input
            type="file"
            accept=".xlsx,.xls,.csv"
            onChange={handleFileChange}
            className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-md file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100"
          />
          {file && (
            <p className="mt-2 text-sm text-green-600">
              ✓ Selected: {file.name}
            </p>
          )}
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Privacy Mode
          </label>
          <select
            value={privacyMode}
            onChange={(e) => setPrivacyMode(e.target.value)}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="strict">Strict (Maximum Privacy)</option>
            <option value="normal">Normal (Balanced)</option>
            <option value="detailed">Detailed (More Analysis)</option>
          </select>
          <p className="mt-1 text-xs text-gray-500">
            🔒 All modes process data 100% locally - no external API calls
          </p>
        </div>

        <button
          onClick={handleAnalyze}
          disabled={!file || loading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {loading ? 'Analyzing...' : '🔍 Analyze File (Preview)'}
        </button>
      </div>

      {analysis && (
        <>
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Analysis Results</h2>
            
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="bg-blue-50 p-4 rounded">
                <p className="text-sm text-gray-600">Categories</p>
                <p className="text-2xl font-bold text-blue-600">{analysis.stats.categories}</p>
              </div>
              <div className="bg-green-50 p-4 rounded">
                <p className="text-sm text-gray-600">Total Tasks</p>
                <p className="text-2xl font-bold text-green-600">{analysis.stats.total_tasks}</p>
              </div>
            </div>

            <div className="bg-green-50 border border-green-200 rounded p-4 mb-4">
              <h3 className="font-semibold text-green-800 mb-2">🔒 Privacy Assurance</h3>
              <ul className="text-sm text-green-700 space-y-1">
                <li>✓ Processing: {analysis.privacy.processing}</li>
                <li>✓ External API Calls: {analysis.privacy.external_api_calls}</li>
                <li>✓ Data Transmitted: {analysis.privacy.data_transmitted ? 'Yes' : 'No'}</li>
                <li>✓ Audit Entries: {analysis.privacy.audit_entries}</li>
              </ul>
            </div>

            <div className="mb-4">
              <h3 className="font-semibold mb-2">Categories Preview:</h3>
              <div className="space-y-2">
                {analysis.preview.categories.map((cat, idx) => (
                  <div key={idx} className="border border-gray-200 rounded p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">{cat.name}</span>
                      <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                        {cat.type} | {cat.tasks.length} tasks
                      </span>
                    </div>
                    <div className="text-sm text-gray-600">
                      {cat.tasks.slice(0, 3).map((task, tidx) => (
                        <span key={tidx} className="inline-block bg-gray-50 px-2 py-1 rounded mr-2 mb-1">
                          {task.name}
                        </span>
                      ))}
                      {cat.tasks.length > 3 && (
                        <span className="text-gray-400">+{cat.tasks.length - 3} more</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gray-50 p-4 rounded text-sm whitespace-pre-wrap font-mono">
              {analysis.analysis}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Step 2: Create Project</h2>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Project Name *
              </label>
              <input
                type="text"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="E-Commerce Platform"
              />
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description (Optional)
              </label>
              <textarea
                value={projectDescription}
                onChange={(e) => setProjectDescription(e.target.value)}
                rows="3"
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Main e-commerce project with frontend and backend components"
              />
            </div>

            <button
              onClick={handleUpload}
              disabled={!projectName.trim() || loading}
              className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating...' : '✓ Create Project'}
            </button>
          </div>
        </>
      )}

      {loading && <Loader />}
    </div>
  );
}
