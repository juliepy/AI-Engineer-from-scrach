import React, { useEffect, useState } from 'react';
import { QAHistory } from '../../../shared/types';

/**
 * ConversationHistory -- solution version.
 *
 * Full chat-style display with:
 * - Chat bubbles distinguishing user questions from assistant answers
 * - Expandable citations
 * - Confidence indicator
 * - Timestamps
 * - Feedback buttons (thumbs up/down)
 * - Clear history action
 */
export function ConversationHistory() {
  const [history, setHistory] = useState<QAHistory[]>([]);
  const [expandedCitations, setExpandedCitations] = useState<Set<number>>(new Set());

  useEffect(() => {
    window.knowledgeBase.qa.history().then(setHistory);
  }, []);

  const toggleCitation = (index: number) => {
    setExpandedCitations(prev => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  };

  const handleClearHistory = async () => {
    if (window.confirm('Clear all conversation history? This cannot be undone.')) {
      await window.knowledgeBase.qa.clearHistory();
      setHistory([]);
    }
  };

  const handleFeedback = async (qaTimestamp: string, question: string, rating: 'positive' | 'negative') => {
    await window.knowledgeBase.feedback.submit(qaTimestamp, question, rating);
  };

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
        <h3 style={{ fontSize: '16px', fontWeight: 600 }}>
          Conversation History ({history.length} exchanges)
        </h3>
        <button
          onClick={handleClearHistory}
          style={{
            padding: '4px 10px',
            background: '#5a2d2d',
            color: '#d9534f',
            border: '1px solid #7a3d3d',
            borderRadius: '3px',
            cursor: 'pointer',
            fontSize: '12px',
          }}
        >
          Clear History
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {history.map((item, index) => {
          const isExpanded = expandedCitations.has(index);
          const confidencePercent = (item.response.confidence * 100).toFixed(0);
          const confidenceColor = item.response.confidence >= 0.7 ? '#5cb85c' : item.response.confidence >= 0.5 ? '#f0ad4e' : '#d9534f';

          return (
            <div key={index}>
              {/* User question bubble */}
              <div style={{
                display: 'flex',
                justifyContent: 'flex-end',
                marginBottom: '4px',
              }}>
                <div style={{
                  maxWidth: '70%',
                  padding: '10px 14px',
                  background: '#533483',
                  borderRadius: '12px 12px 2px 12px',
                  fontSize: '14px',
                  lineHeight: 1.5,
                }}>
                  {item.question}
                </div>
              </div>
              <div style={{
                textAlign: 'right',
                fontSize: '10px',
                color: '#555',
                marginBottom: '4px',
                paddingRight: '4px',
              }}>
                {new Date(item.response.timestamp).toLocaleTimeString()}
              </div>

              {/* Assistant answer bubble */}
              <div style={{
                display: 'flex',
                justifyContent: 'flex-start',
                marginBottom: '4px',
              }}>
                <div style={{
                  maxWidth: '80%',
                  padding: '12px 14px',
                  background: '#1a1a3e',
                  borderRadius: '12px 12px 12px 2px',
                  border: '1px solid #0f3460',
                  fontSize: '14px',
                  lineHeight: 1.6,
                }}>
                  <div>{item.response.answer}</div>

                  {/* Confidence and citation toggle */}
                  <div style={{
                    marginTop: '8px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    fontSize: '11px',
                  }}>
                    <span style={{ color: confidenceColor }}>
                      Confidence: {confidencePercent}%
                    </span>
                    {item.response.citations.length > 0 && (
                      <button
                        onClick={() => toggleCitation(index)}
                        style={{
                          background: 'none',
                          border: 'none',
                          color: '#8888bb',
                          cursor: 'pointer',
                          fontSize: '11px',
                          textDecoration: 'underline',
                        }}
                      >
                        {isExpanded ? 'Hide' : 'Show'} {item.response.citations.length} citation(s)
                      </button>
                    )}
                  </div>

                  {/* Expanded citations */}
                  {isExpanded && item.response.citations.length > 0 && (
                    <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #0f3460' }}>
                      {item.response.citations.map((c, ci) => (
                        <div key={ci} style={{
                          padding: '6px 8px',
                          marginBottom: '4px',
                          background: '#0f1729',
                          borderRadius: '4px',
                          borderLeft: '2px solid #533483',
                          fontSize: '12px',
                          color: '#aaa',
                        }}>
                          <div style={{ color: '#b088f9', marginBottom: '2px' }}>
                            {c.documentTitle} -- chunk {c.chunkIndex}
                          </div>
                          <div style={{ lineHeight: 1.4 }}>{c.excerpt.substring(0, 150)}...</div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Feedback buttons */}
                  <div style={{
                    marginTop: '8px',
                    display: 'flex',
                    gap: '6px',
                    justifyContent: 'flex-end',
                  }}>
                    <button
                      onClick={() => handleFeedback(item.response.timestamp, item.question, 'positive')}
                      style={{
                        padding: '2px 8px',
                        background: 'transparent',
                        border: '1px solid #3d7a3d',
                        borderRadius: '3px',
                        cursor: 'pointer',
                        fontSize: '12px',
                        color: '#5cb85c',
                      }}
                      title="Good answer"
                    >
                      +1
                    </button>
                    <button
                      onClick={() => handleFeedback(item.response.timestamp, item.question, 'negative')}
                      style={{
                        padding: '2px 8px',
                        background: 'transparent',
                        border: '1px solid #7a3d3d',
                        borderRadius: '3px',
                        cursor: 'pointer',
                        fontSize: '12px',
                        color: '#d9534f',
                      }}
                      title="Poor answer"
                    >
                      -1
                    </button>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
