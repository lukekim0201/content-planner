import { useRef, useState } from 'react'
import { uploadAsset } from '../api/client'

export default function AssetUploader({ projectId, onUploaded }) {
  const inputRef = useRef(null)
  const [isDragging, setIsDragging] = useState(false)
  const [uploads, setUploads] = useState([]) // [{ id, name, progress, error }]

  function handleFiles(fileList) {
    const files = Array.from(fileList)
    files.forEach((file) => {
      const uploadId = `${file.name}-${Date.now()}-${Math.random()}`
      setUploads((prev) => [...prev, { id: uploadId, name: file.name, progress: 0, error: null }])

      uploadAsset(projectId, file, (progress) => {
        setUploads((prev) => prev.map((u) => (u.id === uploadId ? { ...u, progress } : u)))
      })
        .then((asset) => {
          setUploads((prev) => prev.filter((u) => u.id !== uploadId))
          onUploaded(asset)
        })
        .catch((err) => {
          setUploads((prev) =>
            prev.map((u) => (u.id === uploadId ? { ...u, error: err.message } : u)),
          )
        })
    })
  }

  return (
    <div>
      <div
        onDragOver={(e) => {
          e.preventDefault()
          setIsDragging(true)
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault()
          setIsDragging(false)
          if (e.dataTransfer.files?.length) handleFiles(e.dataTransfer.files)
        }}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition ${
          isDragging ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <p className="text-sm text-gray-500">
          Drag &amp; drop photos, video, or audio here, or click to browse
        </p>
        <input
          ref={inputRef}
          type="file"
          multiple
          accept="image/*,video/*,audio/*"
          className="hidden"
          onChange={(e) => {
            if (e.target.files?.length) handleFiles(e.target.files)
            e.target.value = ''
          }}
        />
      </div>

      {uploads.length > 0 && (
        <ul className="mt-2 space-y-1">
          {uploads.map((u) => (
            <li key={u.id} className="text-xs">
              {u.error ? (
                <span className="text-red-600">
                  {u.name}: {u.error}
                </span>
              ) : (
                <div className="flex items-center gap-2">
                  <span className="text-gray-500 truncate max-w-[10rem]">{u.name}</span>
                  <div className="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-500 transition-all"
                      style={{ width: `${u.progress}%` }}
                    />
                  </div>
                  <span className="text-gray-400">{u.progress}%</span>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
