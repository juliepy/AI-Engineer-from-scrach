import React, { useEffect, useState } from 'react';
import { QAHistory } from '../../../shared/types';

/**
 * ConversationHistory -- starter version.
 *
 * Displays Q&A history as a simple list.
 * The solution version adds chat bubbles, citation expansion,
 * follow-up suggestions, and feedback buttons.
 */
export function ConversationHistory() {
  const [history, setHistory] = useState<QAHistory[]>([]);

  useEffect(() => {
    window.knowledgeBase.qa.history().then(setHistory);
  }, []);

  if (history.length === 0) {
    return (
      <div style={{ color: '#666', textAlign: 'center', paddingTop: '40px' }}>
        No conversation history yet. Ask a question to get started.
      </div>
    );
  }

  return (
    <div>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '16px',
      }}>
        <h3 style={{ fontSize: '16px', fontWeight: 600 }}>Conversation History</h3>
        <button
          onClick={() => {
            window.knowledgeBase.qa.clearHistory();
            setHistory([]);
          }}
          style={{
            padding: '4px 10px',
            background: '#d9534f',
            color: '#fff',
            border: 'none',
            borderRadius: '3px',
            cursor: 'pointer',
            fontSize: '12px',
          }}
        >
          Clear History
        </button>
      </div>
      {history.map((item, index) => (
        <div key={index} style={{
          marginBottom: '16px',
          padding: '12px',
          background: '#1a1a3e',
          borderRadius: '6px',
          border: '1px solid #0f3460',
        }}>
          <div style={{ fontSize: '13px', fontWeight: 500, color: '#b088f9' }}>
            Q: {item.question}
          </div>
          <div style={{ fontSize: '13px', marginTop: '8px', lineHeight: 1.5 }}>
            {item.response.answer}
          </div>
          {item.response.citations.length > 0 && (
            <div style={{ marginTop: '6px', fontSize: '11px', color: '#8888bb' }}>
              {item.response.citations.length} citation(s) | Confidence: {(item.response.confidence * 100).toFixed(0)}%
            </div>
          )}
          <div style={{ marginTop: '6px', fontSize: '10px', color: '#555' }}>
            {new Date(item.response.timestamp).toLocaleString()}
          </div>
        </div>
      ))}
    </div>
  );
}
