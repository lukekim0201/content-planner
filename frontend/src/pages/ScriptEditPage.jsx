import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { apiFetch } from '../api/client'
import ScriptEditor from '../components/ScriptEditor'
import SceneSuggestBox from '../components/SceneSuggestBox'

export default function ScriptEditPage() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const [content, setContent] = useState('')
  const [existingScript, setExistingScript] = useState(null)
  const [saving, setSaving] = useState(false)
  const [loaded, setLoaded] = useState(false)
  const [loadError, setLoadError] = useState(null)

  useEffect(() => {
    apiFetch(`/projects/${projectId}/full`)
      .then((project) => {
        if (project.script) {
          setContent(project.script.content)
          setExistingScript(project.script)
        }
        setLoaded(true)
      })
      .catch((err) => setLoadError(err.message))
  }, [projectId])

  async function handleSave() {
    setSaving(true)
    try {
      if (existingScript) {
        await apiFetch(`/projects/${projectId}/script`, {
          method: 'PATCH',
          body: JSON.stringify({ content }),
        })
      } else {
        await apiFetch(`/projects/${projectId}/script`, {
          method: 'POST',
          body: JSON.stringify({ content }),
        })
      }
      navigate(`/projects/${projectId}`)
    } catch (err) {
      alert(err.message)
    } finally {
      setSaving(false)
    }
  }

  if (loadError) return <div className="p-8 text-red-600">{loadError}</div>
  if (!loaded) return <div className="p-8">Loading...</div>

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <Link to={`/projects/${projectId}`} className="text-sm text-gray-500 hover:text-gray-700">
        ← Back to project
      </Link>
      <h1 className="text-xl font-semibold mt-2 mb-4">Edit Script</h1>

      <ScriptEditor content={content} onChange={setContent} />

      <button
        onClick={handleSave}
        disabled={saving}
        className="mt-4 bg-blue-600 text-white rounded px-4 py-2 disabled:opacity-50"
      >
        {saving ? 'Saving...' : 'Save Script'}
      </button>

      {existingScript && (
        <div className="mt-6">
          <SceneSuggestBox projectId={projectId} />
        </div>
      )}
    </div>
  )
}
