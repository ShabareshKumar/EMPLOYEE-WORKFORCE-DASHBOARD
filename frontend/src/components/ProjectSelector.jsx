import { useState, useEffect } from 'react';
import api from '../api/axios';

export default function ProjectSelector({ onSelect, selectedValues = {} }) {
  const [projects, setProjects] = useState([]);
  const [categories, setCategories] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);

  const [selectedProject, setSelectedProject] = useState(selectedValues.projectId || '');
  const [selectedCategory, setSelectedCategory] = useState(selectedValues.categoryId || '');
  const [selectedTask, setSelectedTask] = useState(selectedValues.taskId || '');

  // Load projects on mount
  useEffect(() => {
    loadProjects();
  }, []);

  // Load categories when project changes
  useEffect(() => {
    if (selectedProject) {
      loadCategories(selectedProject);
    } else {
      setCategories([]);
      setTasks([]);
      setSelectedCategory('');
      setSelectedTask('');
    }
  }, [selectedProject]);

  // Load tasks when category changes
  useEffect(() => {
    if (selectedCategory) {
      loadTasks(selectedCategory);
    } else {
      setTasks([]);
      setSelectedTask('');
    }
  }, [selectedCategory]);

  // Notify parent when selection is complete
  useEffect(() => {
    if (selectedProject && selectedCategory && selectedTask) {
      onSelect({
        projectId: parseInt(selectedProject),
        categoryId: parseInt(selectedCategory),
        taskId: parseInt(selectedTask)
      });
    }
  }, [selectedProject, selectedCategory, selectedTask, onSelect]);

  const loadProjects = async () => {
    setLoading(true);
    try {
      const response = await api.get('/projects');
      setProjects(response.data.projects || []);
    } catch (error) {
      console.error('Failed to load projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCategories = (projectId) => {
    const project = projects.find(p => p.id === parseInt(projectId));
    if (project) {
      setCategories(project.categories || []);
    }
  };

  const loadTasks = (categoryId) => {
    const category = categories.find(c => c.id === parseInt(categoryId));
    if (category) {
      setTasks(category.tasks || []);
    }
  };

  const handleProjectChange = (e) => {
    setSelectedProject(e.target.value);
    setSelectedCategory('');
    setSelectedTask('');
  };

  const handleCategoryChange = (e) => {
    setSelectedCategory(e.target.value);
    setSelectedTask('');
  };

  const handleTaskChange = (e) => {
    setSelectedTask(e.target.value);
  };

  return (
    <div className="space-y-4">
      {/* Project Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Project *
        </label>
        <select
          value={selectedProject}
          onChange={handleProjectChange}
          disabled={loading}
          className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Select a project...</option>
          {projects.map(project => (
            <option key={project.id} value={project.id}>
              {project.name}
            </option>
          ))}
        </select>
      </div>

      {/* Category Selection */}
      {selectedProject && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Category *
          </label>
          <select
            value={selectedCategory}
            onChange={handleCategoryChange}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Select a category...</option>
            {categories.map(category => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Task Selection */}
      {selectedCategory && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Task *
          </label>
          <select
            value={selectedTask}
            onChange={handleTaskChange}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Select a task...</option>
            {tasks.map(task => (
              <option key={task.id} value={task.id}>
                {task.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Selection Summary */}
      {selectedProject && selectedCategory && selectedTask && (
        <div className="bg-green-50 border border-green-200 rounded p-3">
          <p className="text-sm text-green-800">
            ✓ Selected: {projects.find(p => p.id === parseInt(selectedProject))?.name} → {' '}
            {categories.find(c => c.id === parseInt(selectedCategory))?.name} → {' '}
            {tasks.find(t => t.id === parseInt(selectedTask))?.name}
          </p>
        </div>
      )}
    </div>
  );
}
