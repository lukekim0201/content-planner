import { useParams, Link, useNavigate } from 'react-router-dom'
import { apiFetch } from '../api/client'
import { useApi } from '../hooks/useApi'

export default function ProjectDetailPage() {
  const { projectId } = useParams()
  const navigate = useNavigate()

  const { data: project, loading, error, refetch } = useApi(`/projects/${projectId}/full`)

  async function handleDelete() {
    if (!confirm('Delete this project? This cannot be undone.')) return
    try {
      await apiFetch(`/projects/${projectId}`, { method: 'DELETE' })
      navigate('/dashboard')
    } catch (err) {
      alert(err.message)
    }
  }

  async function handleTitleUpdate(newTitle) {
    try {
      await apiFetch(`/projects/${projectId}`, {
        method: 'PATCH',
        body: JSON.stringify({ title: newTitle }),
      })
      refetch()
    } catch (err) {
      alert(err.message)
    }
  }

  function handleTitleClick() {
    const newTitle = prompt('Edit title:', project.title)
    if (newTitle && newTitle.trim() && newTitle.trim() !== project.title) {
      handleTitleUpdate(newTitle.trim())
    }
  }

  if (loading) return <div className="p-8">Loading...</div>
  if (error) return <div className="p-8 text-red-600">{error}</div>

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <h1
          className="text-2xl font-semibold cursor-pointer hover:underline"
          onClick={handleTitleClick}
          title="Click to edit"
        >
          {project.title}
        </h1>
        <div className="flex items-center gap-3">
          <span className="text-xs uppercase text-gray-500">{project.status}</span>
          <button onClick={handleDelete} className="text-red-600 text-sm">
            Delete Project
          </button>
        </div>
      </div>

      <section className="mb-8">
        <div className="flex justify-between items-center mb-2">
          <h2 className="font-medium text-lg">Script</h2>
          <Link
            to={`/projects/${projectId}/script/edit`}
            className="text-blue-600 text-sm"
          >
            {project.script ? 'Edit' : 'Write script'}
          </Link>
        </div>
        {project.script ? (
          <div
            className="prose border rounded p-4"
            dangerouslySetInnerHTML={{ __html: project.script.content }}
          />
        ) : (
          <p className="text-gray-500">No script yet.</p>
        )}
      </section>

      <section>
        <h2 className="font-medium text-lg mb-2">Assets ({project.assets.length})</h2>
        {project.assets.length === 0 ? (
          <p className="text-gray-500">No assets uploaded yet.</p>
        ) : (
          <ul className="grid grid-cols-3 gap-3">
            {project.assets.map((asset) => (
              <li key={asset.id} className="border rounded p-2 text-xs truncate">
                {asset.asset_type} — {asset.file_url}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}