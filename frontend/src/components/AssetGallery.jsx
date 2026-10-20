import { apiFetch } from '../api/client'

function AssetPreview({ asset }) {
  switch (asset.asset_type) {
    case 'IMAGE':
      return (
        <img
          src={asset.file_url}
          alt={asset.file_name}
          className="w-full h-28 object-cover rounded"
          loading="lazy"
        />
      )
    case 'VIDEO':
      return <video src={asset.file_url} controls className="w-full h-28 rounded bg-black" />
    case 'AUDIO':
      return (
        <div className="w-full h-28 rounded bg-gray-100 flex items-center justify-center px-2">
          <audio src={asset.file_url} controls className="w-full" />
        </div>
      )
    default:
      return (
        <div className="w-full h-28 rounded bg-gray-100 flex items-center justify-center text-2xl">
          📄
        </div>
      )
  }
}

function formatSize(bytes) {
  if (!bytes) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function AssetGallery({ projectId, assets, onDeleted }) {
  async function handleDelete(assetId) {
    if (!confirm('Delete this asset?')) return
    try {
      await apiFetch(`/projects/${projectId}/assets/${assetId}`, { method: 'DELETE' })
      onDeleted(assetId)
    } catch (err) {
      alert(err.message)
    }
  }

  if (assets.length === 0) {
    return <p className="text-gray-500 text-sm">No assets uploaded yet.</p>
  }

  return (
    <ul className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
      {assets.map((asset) => (
        <li key={asset.id} className="group relative border border-gray-200 rounded-lg p-2">
          <AssetPreview asset={asset} />
          <p className="text-xs text-gray-600 truncate mt-1" title={asset.file_name}>
            {asset.file_name || asset.asset_type}
          </p>
          <p className="text-[10px] text-gray-400">{formatSize(asset.size_bytes)}</p>
          <button
            onClick={() => handleDelete(asset.id)}
            title="Delete asset"
            className="absolute top-1 right-1 bg-white/90 text-red-600 rounded-full w-6 h-6 text-xs opacity-0 group-hover:opacity-100 transition border border-gray-200"
          >
            ✕
          </button>
        </li>
      ))}
    </ul>
  )
}
