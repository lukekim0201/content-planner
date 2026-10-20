import { Link } from 'react-router-dom'

export default function ProjectCard({ project, onDragStart }) {
  return (
    <Link
      to={`/projects/${project.id}`}
      draggable
      onDragStart={(e) => {
        e.dataTransfer.setData('text/plain', project.id)
        e.dataTransfer.effectAllowed = 'move'
        onDragStart?.(project.id)
      }}
      className="block bg-white border border-gray-200 rounded-lg p-3 shadow-sm hover:shadow-md hover:border-gray-300 transition cursor-grab active:cursor-grabbing"
    >
      <h3 className="font-medium text-sm text-gray-900 truncate">{project.title}</h3>
      <p className="text-xs text-gray-400 mt-1">
        {new Date(project.created_at).toLocaleDateString()}
      </p>
    </Link>
  )
}
