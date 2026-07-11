import React from 'react';
import { QAHistory } from '../../../shared/types';

interface Props {
  history: QAHistory[];
  onSelect?: (item: QAHistory) => void;
}

/**
 * ConversationHistory - Generator + Evaluator implementation
 *
 * Improved conversation display with chat bubbles, timestamps,
 * and citation previews. Reviewed by an evaluator agent.
 */
export function ConversationHistory({ history, onSelect }: Props) {
  if (history.length === 0) {
    return (
      <div style={{
        padding: '40px 20px',
        color: '#666',
        textAlign: 'center',
        fontSize: '13px',
      }}>
        <div style={{ fontSize: '24px', marginBottom: '8px' }}>&#128172;</div>
        No conversation history yet.
        <br />
        <span style={{ fontSize: '11px', color: '#555' }}>
          Ask a question to start a conversation.
        </span>
      </div>
    );
  }

  return (
    <div style={{ flex: 1, overflow: 'auto', padding: '8px' }}>
      {history.map((item, i) => {
        const time = new Date(item.response.timestamp);
        const timeStr = time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        return (
          <div key={i} style={{ marginBottom: '10px' }}>
            {/* User question bubble */}
            <div style={{
              display: 'flex',
              justifyContent: 'flex-end',
              marginBottom: '4px',
            }}>
              <div
                onClick={() => onSelect?.(item)}
                style={{
                  maxWidth: '85%',
                  padding: '8px 12px',
                  background: '#533483',
                  color: '#fff',
                  borderRadius: '12px 12px 2px 12px',
                  fontSize: '12px',
                  lineHeight: 1.4,
                  cursor: onSelect ? 'pointer' : 'default',
                }}
              >
                {item.question}
              </div>
            </div>

            {/* Assistant answer bubble */}
            <div style={{
              display: 'flex',
              justifyContent: 'flex-start',
              marginBottom: '2px',
            }}>
              <div style={{
                maxWidth: '85%',
                padding: '8px 12px',
                background: '#1a1a3e',
                color: '#e0e0e0',
                borderRadius: '12px 12px 12px 2px',
                fontSize: '11px',
                lineHeight: 1.5,
              }}>
                {item.response.answer.substring(0, 120)}
                {item.response.answer.length > 120 ? '...' : ''}

                {item.response.citations.length > 0 && (
                  <div style={{
                    marginTop: '6px',
                    fontSize: '10px',
                    color: '#8888bb',
                    borderTop: '1px solid #0f3460',
                    paddingTop: '4px',
                  }}>
                    {item.response.citations.length} citation(s)
                  </div>
                )}
              </div>
            </div>

            {/* Timestamp */}
            <div style={{
              fontSize: '10px',
              color: '#555',
              textAlign: 'center',
              padding: '0 4px',
            }}>
              {timeStr}
            </div>
          </div>
        );
      })}
    </div>
  );
}
