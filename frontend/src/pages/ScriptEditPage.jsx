import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { apiFetch } from '../api/client'
import ScriptEditor from '../components/ScriptEditor'

export default function ScriptEditPage() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const [content, setContent] = useState('')
  const [existingScript, setExistingScript] = useState(null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    apiFetch(`/projects/${projectId}/full`).then((project) => {
      if (project.script) {
        setContent(project.script.content)
        setExistingScript(project.script)
      }
    })
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

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <h1 className="text-xl font-semibold mb-4">Edit Script</h1>
      <ScriptEditor content={content} onChange={setContent} />
      <button
        onClick={handleSave}
        disabled={saving}
        className="mt-4 bg-blue-600 text-white rounded px-4 py-2 disabled:opacity-50"
      >
        {saving ? 'Saving...' : 'Save Script'}
      </button>
    </div>
  )
}