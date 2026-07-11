import React, { useEffect, useState } from 'react';
import { Document, Chunk } from '../../../shared/types';

interface Props {
  document: Document;
  onDelete?: (id: string) => void;
}

export function DocumentDetail({ document, onDelete }: Props) {
  const [chunks, setChunks] = useState<Chunk[]>([]);
  const [showChunks, setShowChunks] = useState(false);
  const [content, setContent] = useState<string | null>(null);

  useEffect(() => {
    window.knowledgeBase.indexing.chunks(document.id).then(setChunks);
  }, [document.id]);

  // TODO: Load document content for viewing -- not yet implemented
  // This is part of the document-detail feature to be completed.

  return (
    <div>
      <h2 style={{ fontSize: '20px', fontWeight: 600, marginBottom: '8px' }}>
        {document.title}
      </h2>
      <div style={{ fontSize: '13px', color: '#888', marginBottom: '16px' }}>
        <div>Filename: {document.filename}</div>
        <div>Imported: {new Date(document.importedAt).toLocaleString()}</div>
        <div>Size: {(document.size / 1024).toFixed(1)} KB</div>
        <div>Status: {document.status}</div>
        {document.chunks !== undefined && <div>Chunks: {document.chunks}</div>}
      </div>

      <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
        <button
          onClick={() => setShowChunks(!showChunks)}
          style={{
            padding: '6px 12px',
            background: '#0f3460',
            color: '#e0e0e0',
            border: '1px solid #1a1a4e',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '12px',
          }}
        >
          {showChunks ? 'Hide' : 'Show'} Chunks ({chunks.length})
        </button>
        {document.status !== 'indexed' && (
          <button
            onClick={() => window.knowledgeBase.indexing.start(document.id)}
            style={{
              padding: '6px 12px',
              background: '#533483',
              color: '#fff',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px',
            }}
          >
            Index Document
          </button>
        )}
        {onDelete && (
          <button
            onClick={() => onDelete(document.id)}
            style={{
              padding: '6px 12px',
              background: '#8b2252',
              color: '#fff',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px',
            }}
          >
            Delete
          </button>
        )}
      </div>

      {/* Content viewer -- placeholder until document-detail feature is implemented */}
      {content && (
        <div style={{
          padding: '16px',
          background: '#1a1a3e',
          borderRadius: '6px',
          border: '1px solid #0f3460',
          fontSize: '13px',
          lineHeight: 1.6,
          whiteSpace: 'pre-wrap',
        }}>
          {content}
        </div>
      )}

      {showChunks && (
        <div>
          {chunks.map(chunk => (
            <div
              key={chunk.id}
              style={{
                padding: '10px',
                marginBottom: '8px',
                background: '#1a1a3e',
                borderRadius: '4px',
                borderLeft: '3px solid #533483',
                fontSize: '13px',
                lineHeight: 1.5,
              }}
            >
              <div style={{ fontSize: '11px', color: '#888', marginBottom: '4px' }}>
                Chunk {chunk.index} ({chunk.metadata.charCount} chars)
              </div>
              {chunk.content}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
