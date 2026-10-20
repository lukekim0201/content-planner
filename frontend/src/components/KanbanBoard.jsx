import { useState } from 'react'
import ProjectCard from './ProjectCard'

export const COLUMNS = [
  { status: 'IDEA', label: 'Idea', accent: 'border-t-gray-400' },
  { status: 'SCRIPTING', label: 'Scripting', accent: 'border-t-blue-400' },
  { status: 'PRODUCTION', label: 'Production', accent: 'border-t-amber-400' },
  { status: 'COMPLETED', label: 'Completed', accent: 'border-t-green-500' },
]

export default function KanbanBoard({ projects, onStatusChange }) {
  const [dragOverStatus, setDragOverStatus] = useState(null)

  function handleDrop(e, status) {
    e.preventDefault()
    setDragOverStatus(null)
    const projectId = e.dataTransfer.getData('text/plain')
    const project = projects.find((p) => p.id === projectId)
    if (project && project.status !== status) {
      onStatusChange(projectId, status)
    }
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {COLUMNS.map((column) => {
        const columnProjects = projects.filter((p) => p.status === column.status)
        const isDragOver = dragOverStatus === column.status

        return (
          <div
            key={column.status}
            onDragOver={(e) => {
              e.preventDefault()
              setDragOverStatus(column.status)
            }}
            onDragLeave={() => setDragOverStatus((s) => (s === column.status ? null : s))}
            onDrop={(e) => handleDrop(e, column.status)}
            className={`rounded-lg border-t-4 ${column.accent} bg-gray-50 p-3 min-h-[16rem] transition ${
              isDragOver ? 'ring-2 ring-blue-400 bg-blue-50' : ''
            }`}
          >
            <div className="flex items-center justify-between mb-3 px-1">
              <h2 className="font-semibold text-sm text-gray-700">{column.label}</h2>
              <span className="text-xs text-gray-400 bg-white rounded-full px-2 py-0.5 border border-gray-200">
                {columnProjects.length}
              </span>
            </div>
            <div className="flex flex-col gap-2">
              {columnProjects.map((project) => (
                <ProjectCard key={project.id} project={project} />
              ))}
              {columnProjects.length === 0 && (
                <p className="text-xs text-gray-400 text-center py-6">Drop a project here</p>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
