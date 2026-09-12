import { useState } from 'react'
import { useStore } from '@/store'
import { cn } from '@/lib/utils'
import {
  Folder,
  FolderOpen,
  FileText,
  ChevronRight,
  ChevronDown,
} from 'lucide-react'
import type { FileNode } from '@/types'

interface FileTreeProps {
  onFileSelect?: (path: string) => void
}

export function FileTree({ onFileSelect }: FileTreeProps) {
  const { files, selectedFile, setSelectedFile } = useStore()

  const handleSelect = (path: string) => {
    setSelectedFile(path)
    onFileSelect?.(path)
  }

  return (
    <div className="py-2">
      {files.map(node => (
        <FileTreeNode
          key={node.path}
          node={node}
          depth={0}
          selectedFile={selectedFile}
          onSelect={handleSelect}
        />
      ))}
    </div>
  )
}

interface FileTreeNodeProps {
  node: FileNode
  depth: number
  selectedFile: string | null
  onSelect: (path: string) => void
}

function FileTreeNode({
  node,
  depth,
  selectedFile,
  onSelect,
}: FileTreeNodeProps) {
  const [expanded, setExpanded] = useState(depth < 1)
  const isFolder = node.type === 'folder'
  const isSelected = selectedFile === node.path

  const handleClick = () => {
    if (isFolder) {
      setExpanded(!expanded)
    } else {
      onSelect(node.path)
    }
  }

  return (
    <div>
      <button
        onClick={handleClick}
        className={cn(
          'flex w-full items-center gap-1.5 rounded-md px-2 py-1 text-sm transition-colors',
          isSelected
            ? 'bg-primary/10 text-primary'
            : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
        )}
        style={{ paddingLeft: `${depth * 12 + 8}px` }}
      >
        {isFolder ? (
          <>
            {expanded ? (
              <ChevronDown size={14} className="shrink-0" />
            ) : (
              <ChevronRight size={14} className="shrink-0" />
            )}
            {expanded ? (
              <FolderOpen size={16} className="shrink-0 text-yellow-400" />
            ) : (
              <Folder size={16} className="shrink-0 text-yellow-400" />
            )}
          </>
        ) : (
          <>
            <span className="w-3.5 shrink-0" />
            <FileText size={16} className="shrink-0 text-blue-400" />
            {node.status && (
              <span
                className={cn(
                  'ml-auto h-2 w-2 rounded-full',
                  node.status === 'approved'
                    ? 'bg-green-400'
                    : node.status === 'rejected'
                    ? 'bg-red-400'
                    : node.status === 'reviewing'
                    ? 'bg-blue-400'
                    : 'bg-yellow-400'
                )}
              />
            )}
          </>
        )}
        <span className="truncate">{node.name}</span>
      </button>

      {isFolder && expanded && node.children && (
        <div>
          {node.children.map((child: FileNode) => (
            <FileTreeNode
              key={child.path}
              node={child}
              depth={depth + 1}
              selectedFile={selectedFile}
              onSelect={onSelect}
            />
          ))}
        </div>
      )}
    </div>
  )
}
