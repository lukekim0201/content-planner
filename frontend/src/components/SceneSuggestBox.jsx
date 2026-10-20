import { useState } from 'react'
import { apiFetch } from '../api/client'

/** Stretch goal: ask the backend's optional AI helper what scene might come
 * next. Degrades gracefully — if the server has no OPENAI_API_KEY
 * configured it returns HTTP 501, which we show as a friendly note instead
 * of an error. */
export default function SceneSuggestBox({ projectId }) {
  const [direction, setDirection] = useState('')
  const [suggestion, setSuggestion] = useState(null)
  const [loading, setLoading] = useState(false)
  const [notConfigured, setNotConfigured] = useState(false)
  const [error, setError] = useState(null)

  async function handleSuggest() {
    setLoading(true)
    setError(null)
    setNotConfigured(false)
    setSuggestion(null)
    try {
      const result = await apiFetch(`/projects/${projectId}/script/suggest`, {
        method: 'POST',
        body: JSON.stringify({ direction: direction.trim() || undefined }),
      })
      setSuggestion(result.suggestion)
    } catch (err) {
      if (err.message?.includes("aren't configured")) {
        setNotConfigured(true)
      } else {
        setError(err.message)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="border border-dashed border-purple-300 rounded-lg p-4 bg-purple-50/50">
      <h3 className="text-sm font-medium text-purple-900 mb-2">✨ Suggest the next scene (AI, optional)</h3>
      <div className="flex gap-2">
        <input
          value={direction}
          onChange={(e) => setDirection(e.target.value)}
          placeholder="Optional direction, e.g. 'make it funnier'"
          className="flex-1 border border-gray-300 rounded px-3 py-1.5 text-sm"
        />
        <button
          onClick={handleSuggest}
          disabled={loading}
          className="bg-purple-600 text-white text-sm rounded px-3 py-1.5 disabled:opacity-50"
        >
          {loading ? 'Thinking…' : 'Suggest'}
        </button>
      </div>

      {notConfigured && (
        <p className="text-xs text-gray-500 mt-2">
          This is an optional stretch feature — set <code>OPENAI_API_KEY</code> in the
          backend's <code>.env</code> to turn it on.
        </p>
      )}
      {error && <p className="text-xs text-red-600 mt-2">{error}</p>}
      {suggestion && (
        <p className="text-sm text-gray-800 mt-3 whitespace-pre-wrap bg-white rounded p-3 border border-purple-200">
          {suggestion}
        </p>
      )}
    </div>
  )
}
