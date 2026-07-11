import React from 'react';

interface Props {
  onImport: (filePath: string) => void;
}

export function ImportPanel({ onImport }: Props) {
  return (
    <div style={{
      padding: '20px',
      background: '#16213e',
      borderRadius: '6px',
      border: '1px dashed #0f3460',
      textAlign: 'center',
      color: '#888',
    }}>
      <div style={{ fontSize: '14px', marginBottom: '8px' }}>Import Documents</div>
      <div style={{ fontSize: '12px' }}>
        Use the import button or drag files here.
        <br />
        Supported: .txt, .md files
      </div>
      <input
        type="file"
        accept=".txt,.md"
        onChange={e => {
          const file = e.target.files?.[0];
          if (file) onImport(file.path);
        }}
        style={{ marginTop: '10px' }}
      />
    </div>
  );
}
