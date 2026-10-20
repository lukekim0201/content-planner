import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiFetch } from '../api/client'

export default function ProjectFormPage() {
  const [title, setTitle] = useState('')
  const [error, setError] = useState(null)
  const [saving, setSaving] = useState(false)
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setSaving(true)
    try {
      const project = await apiFetch('/projects', {
        method: 'POST',
        body: JSON.stringify({ title }),
      })
      navigate(`/projects/${project.id}`)
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="p-8 max-w-sm mx-auto flex flex-col gap-3">
      <h1 className="text-xl font-semibold">New Project</h1>
      <p className="text-sm text-gray-500 -mt-2">
        Every project starts as an <span className="font-medium">Idea</span> — write a script to
        move it forward.
      </p>
      <input
        className="border rounded px-3 py-2"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Project title, e.g. 'My Trip to Osaka Vlog'"
        autoFocus
        required
      />
      {error && <p className="text-red-600 text-sm">{error}</p>}
      <button
        className="bg-blue-600 text-white rounded px-3 py-2 disabled:opacity-50"
        type="submit"
        disabled={saving}
      >
        {saving ? 'Creating...' : 'Create Project'}
      </button>
    </form>
  )
}
