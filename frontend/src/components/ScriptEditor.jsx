import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'

// `node` is the Tiptap mark/node name, used to highlight the active button.
const TOOLBAR_BUTTONS = [
  { label: 'B', title: 'Bold', node: 'bold', command: (chain) => chain.toggleBold(), style: 'font-bold' },
  { label: 'I', title: 'Italic', node: 'italic', command: (chain) => chain.toggleItalic(), style: 'italic' },
  { label: 'H2', title: 'Heading', node: 'heading', command: (chain) => chain.toggleHeading({ level: 2 }) },
  { label: '"', title: 'Quote', node: 'blockquote', command: (chain) => chain.toggleBlockquote() },
  { label: '•', title: 'Bullet list', node: 'bulletList', command: (chain) => chain.toggleBulletList() },
  { label: '1.', title: 'Numbered list', node: 'orderedList', command: (chain) => chain.toggleOrderedList() },
]

// With editable={false} this doubles as a safe read-only viewer: Tiptap
// parses the HTML through its schema, so <script> tags and event-handler
// attributes in stored content are dropped instead of rendered.
export default function ScriptEditor({
  content,
  onChange,
  editable = true,
  placeholder = 'Start writing your script…',
}) {
  const editor = useEditor({
    extensions: [StarterKit],
    content: content || '',
    editable,
    // Tiptap v3 doesn't re-render on selection changes by default; without
    // this the toolbar's active-button highlight never updates.
    shouldRerenderOnTransaction: true,
    editorProps: {
      attributes: editable
        ? { class: 'script-prose', 'data-placeholder': placeholder }
        : { class: 'script-prose', style: 'min-height: 0' },
    },
    onUpdate: ({ editor }) => onChange?.(editor.getHTML()),
  })

  if (!editor) return null

  if (!editable) {
    return (
      <div className="border rounded-lg p-4 bg-white">
        <EditorContent editor={editor} />
      </div>
    )
  }

  return (
    <div className="border border-gray-300 rounded-lg overflow-hidden">
      <div className="flex gap-1 border-b border-gray-200 bg-gray-50 px-2 py-1.5">
        {TOOLBAR_BUTTONS.map((btn) => (
          <button
            key={btn.label}
            type="button"
            title={btn.title}
            onClick={() => btn.command(editor.chain().focus()).run()}
            className={`w-8 h-8 text-sm rounded hover:bg-gray-200 ${btn.style || ''} ${
              editor.isActive(btn.node) ? 'bg-gray-200' : ''
            }`}
          >
            {btn.label}
          </button>
        ))}
      </div>
      <div className="p-3">
        <EditorContent editor={editor} />
      </div>
    </div>
  )
}
