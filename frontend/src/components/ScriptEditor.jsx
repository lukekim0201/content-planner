import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'

export default function ScriptEditor({ content, onChange }) {
  const editor = useEditor({
    extensions: [StarterKit],
    content: content || '',
    onUpdate: ({ editor }) => onChange(editor.getHTML()),
  })

  return (
    <div className="border rounded p-3 min-h-[200px]">
      <EditorContent editor={editor} />
    </div>
  )
}