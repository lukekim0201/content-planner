import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiFetch } from '../api/client'

export default function ProjectFormPage() {
  const [title, setTitle] = useState('')
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    try {
      const project = await apiFetch('/projects/', {
        method: 'POST',
        body: JSON.stringify({ title }),
      })
      navigate(`/projects/${project.id}`)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="p-8 max-w-sm mx-auto flex flex-col gap-3">
      <h1 className="text-xl font-semibold">New Project</h1>
      <input
        className="border rounded px-3 py-2"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Project title"
        required
      />
      {error && <p className="text-red-600 text-sm">{error}</p>}
      <button className="bg-blue-600 text-white rounded px-3 py-2" type="submit">
        Create Project
      </button>
    </form>
  )
}