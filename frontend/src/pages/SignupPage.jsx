import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { apiFetch } from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function SignupPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { login } = useAuth()

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await apiFetch('/signup', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
      const loginData = await apiFetch('/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
      login(loginData.access_token)
      navigate('/dashboard')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="max-w-sm mx-auto mt-20 flex flex-col gap-3">
      <h1 className="text-xl font-semibold">Create an account</h1>
      <input
        className="border rounded px-3 py-2"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="email"
        required
      />
      <input
        className="border rounded px-3 py-2"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="password (min 8 characters)"
        minLength={8}
        required
      />
      {error && <p className="text-red-600 text-sm">{error}</p>}
      <button
        className="bg-blue-600 text-white rounded px-3 py-2 disabled:opacity-50"
        type="submit"
        disabled={loading}
      >
        {loading ? 'Creating account...' : 'Sign up'}
      </button>
      <p className="text-sm text-gray-500 text-center">
        Already have an account?{' '}
        <Link to="/login" className="text-blue-600">
          Log in
        </Link>
      </p>
    </form>
  )
}
