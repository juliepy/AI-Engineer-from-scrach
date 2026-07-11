import React from 'react';
import { AppStatus } from '../../../shared/types';

interface Props {
  status: AppStatus;
}

export function StatusBar({ status }: Props) {
  const statusColor = {
    idle: '#888',
    indexing: '#f0ad4e',
    ready: '#5cb85c',
    error: '#d9534f',
  }[status.indexStatus] ?? '#888';

  const statusLabel = {
    idle: 'Not indexed',
    indexing: 'Indexing...',
    ready: 'Ready',
    error: 'Error',
  }[status.indexStatus] ?? status.indexStatus;

  return (
    <div style={{
      padding: '4px 20px',
      background: '#0f1729',
      borderTop: '1px solid #0f3460',
      display: 'flex',
      alignItems: 'center',
      gap: '16px',
      fontSize: '11px',
      color: '#888',
    }}>
      <span>
        <span style={{
          display: 'inline-block',
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          background: statusColor,
          marginRight: '6px',
        }} />
        Index: {statusLabel}
      </span>
      <span>Documents: {status.documentsLoaded}</span>
      <span>Indexed: {status.currentIndexed ?? 0}</span>
      {status.lastActivity && (
        <span>Last activity: {new Date(status.lastActivity).toLocaleTimeString()}</span>
      )}
    </div>
  );
}
