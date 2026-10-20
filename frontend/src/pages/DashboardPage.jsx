import { Link } from 'react-router-dom'
import { useApi } from '../hooks/useApi'
import { apiFetch } from '../api/client'
import KanbanBoard from '../components/KanbanBoard'

export default function DashboardPage() {
  const { data: projects, loading, error, setData } = useApi('/projects')

  async function handleStatusChange(projectId, status) {
    const previousStatus = projects.find((p) => p.id === projectId)?.status
    // Optimistic update so the drag feels instant.
    setData((prev) => prev.map((p) => (p.id === projectId ? { ...p, status } : p)))
    try {
      await apiFetch(`/projects/${projectId}`, {
        method: 'PATCH',
        body: JSON.stringify({ status }),
      })
    } catch (err) {
      // Roll back on failure.
      setData((prev) =>
        prev.map((p) => (p.id === projectId ? { ...p, status: previousStatus } : p)),
      )
      alert(err.message)
    }
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Your Projects</h1>
          <p className="text-sm text-gray-500">Drag a card across columns as it moves through production.</p>
        </div>
        <Link to="/projects/new" className="bg-blue-600 text-white rounded px-4 py-2 text-sm font-medium">
          + New Project
        </Link>
      </div>

      {loading && <p className="text-gray-500">Loading projects…</p>}
      {error && <p className="text-red-600">{error}</p>}

      {projects && (
        projects.length === 0 ? (
          <div className="text-center py-16 border border-dashed border-gray-300 rounded-lg">
            <p className="text-gray-500 mb-3">No projects yet — create your first one.</p>
            <Link to="/projects/new" className="text-blue-600 font-medium">
              + New Project
            </Link>
          </div>
        ) : (
          <KanbanBoard projects={projects} onStatusChange={handleStatusChange} />
        )
      )}
    </div>
  )
}
