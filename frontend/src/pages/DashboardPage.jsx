import { Link } from 'react-router-dom'
import { useApi } from '../hooks/useApi'

export default function DashboardPage() {
  const { data: projects, loading, error, refetch } = useApi('/projects/')

  if (loading) return <div className="p-8">Loading projects...</div>
  if (error) return <div className="p-8 text-red-600">{error}</div>

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold">Your Projects</h1>
        <Link to="/projects/new" className="bg-blue-600 text-white rounded px-4 py-2">
          New Project
        </Link>
      </div>

      {projects.length === 0 ? (
        <p className="text-gray-500">No projects yet — create your first one.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {projects.map((project) => (
            <Link
              key={project.id}
              to={`/projects/${project.id}`}
              className="border rounded p-4 hover:shadow-md transition"
            >
              <h2 className="font-medium">{project.title}</h2>
              <span className="text-xs uppercase text-gray-500">{project.status}</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}