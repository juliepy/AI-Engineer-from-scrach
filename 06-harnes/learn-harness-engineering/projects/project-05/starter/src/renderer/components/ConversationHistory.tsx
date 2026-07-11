import React from 'react';
import { QAHistory } from '../../../shared/types';

interface Props {
  history: QAHistory[];
}

/**
 * ConversationHistory - Placeholder component
 *
 * TODO: Implement a full multi-turn conversation history view.
 * For now this displays a basic list of past Q&A exchanges.
 */
export function ConversationHistory({ history }: Props) {
  if (history.length === 0) {
    return (
      <div style={{ padding: '20px', color: '#666', textAlign: 'center', fontSize: '13px' }}>
        No conversation history yet. Ask a question to get started.
      </div>
    );
  }

  return (
    <div style={{ padding: '12px' }}>
      <div style={{ fontSize: '13px', color: '#888', marginBottom: '8px' }}>
        History ({history.length})
      </div>
      {history.map((item, i) => (
        <div key={i} style={{ marginBottom: '8px', fontSize: '12px' }}>
          <div style={{ color: '#a0a0c0' }}>Q: {item.question}</div>
          <div style={{ color: '#888' }}>A: {item.response.answer.substring(0, 80)}...</div>
        </div>
      ))}
    </div>
  );
}
