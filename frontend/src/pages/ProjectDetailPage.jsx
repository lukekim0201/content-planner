import { useParams, Link, useNavigate } from 'react-router-dom'
import { apiFetch } from '../api/client'
import { useApi } from '../hooks/useApi'
import AssetUploader from '../components/AssetUploader'
import AssetGallery from '../components/AssetGallery'
import { COLUMNS } from '../components/KanbanBoard'

export default function ProjectDetailPage() {
  const { projectId } = useParams()
  const navigate = useNavigate()

  const { data: project, loading, error, refetch, setData } = useApi(`/projects/${projectId}/full`)

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

  async function handleStatusSelect(e) {
    const status = e.target.value
    try {
      await apiFetch(`/projects/${projectId}`, {
        method: 'PATCH',
        body: JSON.stringify({ status }),
      })
      setData((prev) => ({ ...prev, status }))
    } catch (err) {
      alert(err.message)
    }
  }

  function handleAssetUploaded(asset) {
    setData((prev) => ({ ...prev, assets: [asset, ...prev.assets] }))
  }

  function handleAssetDeleted(assetId) {
    setData((prev) => ({ ...prev, assets: prev.assets.filter((a) => a.id !== assetId) }))
  }

  if (loading) return <div className="p-8">Loading...</div>
  if (error) return <div className="p-8 text-red-600">{error}</div>

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <Link to="/dashboard" className="text-sm text-gray-500 hover:text-gray-700">
        ← Back to board
      </Link>

      <div className="flex justify-between items-center mt-2 mb-6">
        <h1
          className="text-2xl font-semibold cursor-pointer hover:underline"
          onClick={handleTitleClick}
          title="Click to edit"
        >
          {project.title}
        </h1>
        <div className="flex items-center gap-3">
          <select
            value={project.status}
            onChange={handleStatusSelect}
            className="text-xs uppercase border border-gray-300 rounded px-2 py-1 bg-white"
          >
            {COLUMNS.map((c) => (
              <option key={c.status} value={c.status}>
                {c.label}
              </option>
            ))}
          </select>
          <button onClick={handleDelete} className="text-red-600 text-sm">
            Delete Project
          </button>
        </div>
      </div>

      <section className="mb-8">
        <div className="flex justify-between items-center mb-2">
          <h2 className="font-medium text-lg">Script</h2>
          <Link to={`/projects/${projectId}/script/edit`} className="text-blue-600 text-sm">
            {project.script ? 'Edit' : 'Write script'}
          </Link>
        </div>
        {project.script ? (
          <div
            className="script-prose border rounded-lg p-4 bg-white"
            dangerouslySetInnerHTML={{ __html: project.script.content }}
          />
        ) : (
          <p className="text-gray-500">No script yet.</p>
        )}
      </section>

      <section>
        <h2 className="font-medium text-lg mb-2">Assets ({project.assets.length})</h2>
        <div className="mb-3">
          <AssetUploader projectId={projectId} onUploaded={handleAssetUploaded} />
        </div>
        <AssetGallery projectId={projectId} assets={project.assets} onDeleted={handleAssetDeleted} />
      </section>
    </div>
  )
}
