import React from 'react';
import { Document } from '../../../shared/types';

interface Props {
  documents: Document[];
  onSelect: (doc: Document) => void;
  selectedId: string | null;
}

export function DocumentList({ documents, onSelect, selectedId }: Props) {
  if (documents.length === 0) {
    return (
      <div style={{ padding: '20px 16px', color: '#666', fontSize: '13px', textAlign: 'center' }}>
        No documents imported yet.
        <br />
        <span style={{ fontSize: '11px', color: '#555' }}>
          Import documents to get started.
        </span>
      </div>
    );
  }

  return (
    <div style={{ flex: 1, overflow: 'auto' }}>
      {documents.map(doc => (
        <div
          key={doc.id}
          onClick={() => onSelect(doc)}
          style={{
            padding: '10px 16px',
            cursor: 'pointer',
            borderBottom: '1px solid #0f3460',
            background: selectedId === doc.id ? '#0f3460' : 'transparent',
            transition: 'background 0.15s',
          }}
        >
          <div style={{ fontSize: '13px', fontWeight: 500 }}>{doc.title}</div>
          <div style={{ fontSize: '11px', color: '#888', marginTop: '2px' }}>
            {doc.status === 'indexed' ? 'Indexed ' : ''}
            {(doc.size / 1024).toFixed(1)} KB
          </div>
        </div>
      ))}
    </div>
  );
}
