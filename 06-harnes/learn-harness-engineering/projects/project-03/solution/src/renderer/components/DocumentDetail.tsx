import React, { useEffect, useState } from 'react';
import { Document, Chunk, DocumentMetadata } from '../../../shared/types';

interface Props {
  document: Document;
  onDelete?: (id: string) => void;
  onIndex?: (id: string) => void;
}

export function DocumentDetail({ document, onDelete, onIndex }: Props) {
  const [chunks, setChunks] = useState<Chunk[]>([]);
  const [showChunks, setShowChunks] = useState(false);
  const [content, setContent] = useState<string | null>(null);
  const [showContent, setShowContent] = useState(false);
  const [loadingContent, setLoadingContent] = useState(false);

  useEffect(() => {
    window.knowledgeBase.indexing.chunks(document.id).then(setChunks);
  }, [document.id]);

  // Load document content when requested
  const loadContent = async () => {
    if (content) {
      setShowContent(!showContent);
      return;
    }
    setLoadingContent(true);
    try {
      const text = await window.knowledgeBase.documents.getContent(document.id);
      setContent(text);
      setShowContent(true);
    } catch (err) {
      console.error('Failed to load document content:', err);
    } finally {
      setLoadingContent(false);
    }
  };

  const handleIndex = () => {
    if (onIndex) {
      onIndex(document.id);
    }
  };

  return (
    <div>
      <h2 style={{ fontSize: '20px', fontWeight: 600, marginBottom: '8px' }}>
        {document.title}
      </h2>

      {/* Document metadata */}
      <div style={{ fontSize: '13px', color: '#888', marginBottom: '8px' }}>
        <div>Filename: {document.filename}</div>
        <div>Imported: {new Date(document.importedAt).toLocaleString()}</div>
        <div>Size: {(document.size / 1024).toFixed(1)} KB</div>
        <div>Status: <span style={{ color: document.status === 'indexed' ? '#5cb85c' : '#f0ad4e' }}>{document.status}</span></div>
        {document.chunks !== undefined && <div>Chunks: {document.chunks}</div>}
      </div>

      {/* Extracted metadata section */}
      {document.metadata && (
        <div style={{
          fontSize: '12px',
          color: '#a0a0c0',
          marginBottom: '16px',
          padding: '10px 12px',
          background: '#1a1a3e',
          borderRadius: '4px',
          border: '1px solid #0f3460',
        }}>
          <div style={{ fontWeight: 500, marginBottom: '4px', color: '#c0c0e0' }}>Metadata</div>
          <MetadataRow label="File Type" value={document.metadata.fileType} />
          <MetadataRow label="Words" value={String(document.metadata.wordCount)} />
          <MetadataRow label="Lines" value={String(document.metadata.lineCount)} />
          <MetadataRow label="Paragraphs" value={String(document.metadata.paragraphCount)} />
          <MetadataRow label="Characters" value={String(document.metadata.charCount)} />
        </div>
      )}

      <div style={{ display: 'flex', gap: '8px', marginBottom: '16px', flexWrap: 'wrap' }}>
        <button
          onClick={loadContent}
          disabled={loadingContent}
          style={{
            padding: '6px 12px',
            background: '#0f3460',
            color: '#e0e0e0',
            border: '1px solid #1a1a4e',
            borderRadius: '4px',
            cursor: loadingContent ? 'wait' : 'pointer',
            fontSize: '12px',
          }}
        >
          {loadingContent ? 'Loading...' : showContent ? 'Hide Content' : 'View Content'}
        </button>
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
            onClick={handleIndex}
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

      {/* Document content viewer */}
      {showContent && content && (
        <div style={{
          padding: '16px',
          background: '#1a1a3e',
          borderRadius: '6px',
          border: '1px solid #0f3460',
          fontSize: '13px',
          lineHeight: 1.6,
          whiteSpace: 'pre-wrap',
          maxHeight: '400px',
          overflow: 'auto',
          marginBottom: '16px',
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
                Chunk {chunk.index} ({chunk.metadata.charCount} chars, {chunk.metadata.wordCount} words)
              </div>
              {chunk.content}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function MetadataRow({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: 'flex', gap: '8px' }}>
      <span style={{ color: '#888', minWidth: '80px' }}>{label}:</span>
      <span>{value}</span>
    </div>
  );
}
