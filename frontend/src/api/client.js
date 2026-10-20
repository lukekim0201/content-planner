const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function apiFetch(path, options = {}) {
  const token = localStorage.getItem('token')
  const isFormData = options.body instanceof FormData

  const headers = {
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  }

  const response = await fetch(`${BASE_URL}${path}`, { ...options, headers })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail || `Request failed with status ${response.status}`)
  }

  return response.status === 204 ? null : response.json()
}

export function uploadAsset(projectId, file, onProgress) {
  // Plain fetch has no upload-progress event, so this one path uses
  // XMLHttpRequest instead — everything else in the app goes through
  // apiFetch above.
  const token = localStorage.getItem('token')
  const formData = new FormData()
  formData.append('file', file)

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('POST', `${BASE_URL}/projects/${projectId}/assets/upload`)
    if (token) xhr.setRequestHeader('Authorization', `Bearer ${token}`)

    xhr.upload.onprogress = (event) => {
      if (onProgress && event.lengthComputable) {
        onProgress(Math.round((event.loaded / event.total) * 100))
      }
    }
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.responseText))
      } else {
        let detail = `Upload failed with status ${xhr.status}`
        try {
          detail = JSON.parse(xhr.responseText).detail || detail
        } catch {
          // ignore parse errors, keep default message
        }
        reject(new Error(detail))
      }
    }
    xhr.onerror = () => reject(new Error('Upload failed — network error'))
    xhr.send(formData)
  })
}
