import React from 'react';
import { QAHistory } from '../../../shared/types';

interface Props {
  history: QAHistory[];
}

/**
 * ConversationHistory - Single-role implementation
 *
 * Basic conversation display with simple formatting.
 * One agent did everything without external review.
 */
export function ConversationHistory({ history }: Props) {
  if (history.length === 0) {
    return (
      <div style={{ padding: '20px', color: '#666', textAlign: 'center', fontSize: '13px' }}>
        No conversation history yet.
      </div>
    );
  }

  return (
    <div style={{ flex: 1, overflow: 'auto', padding: '8px' }}>
      {history.map((item, i) => (
        <div key={i} style={{
          marginBottom: '12px',
          padding: '8px',
          background: '#1a1a3e',
          borderRadius: '4px',
        }}>
          <div style={{ fontSize: '12px', color: '#a0a0c0', marginBottom: '4px', fontWeight: 500 }}>
            {item.question}
          </div>
          <div style={{ fontSize: '11px', color: '#888', lineHeight: 1.4 }}>
            {item.response.answer.substring(0, 100)}...
          </div>
          <div style={{ fontSize: '10px', color: '#666', marginTop: '4px' }}>
            {new Date(item.response.timestamp).toLocaleString()}
          </div>
        </div>
      ))}
    </div>
  );
}
