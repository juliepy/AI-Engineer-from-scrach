import React, { useState } from 'react';
import { QAHistory, Citation } from '../../../shared/types';

interface Props {
  history: QAHistory[];
  onSelect?: (item: QAHistory) => void;
  onFollowUp?: (question: string) => void;
}

/**
 * ConversationHistory - Planner + Generator + Evaluator implementation
 *
 * Full-featured conversation display with:
 * - Chat bubbles with user/assistant styling
 * - Timestamps
 * - Citation previews with expand/collapse
 * - "Ask follow-up" suggestions
 * - Copy-to-clipboard for answers
 */
export function ConversationHistory({ history, onSelect, onFollowUp }: Props) {
  const [expandedCitations, setExpandedCitations] = useState<Set<number>>(new Set());
  const [copiedId, setCopiedId] = useState<number | null>(null);

  if (history.length === 0) {
    return (
      <div style={{
        padding: '40px 20px',
        color: '#666',
        textAlign: 'center',
        fontSize: '13px',
      }}>
        <div style={{ fontSize: '28px', marginBottom: '8px' }}>&#128172;</div>
        <div style={{ fontWeight: 500, marginBottom: '4px' }}>No conversation history</div>
        <span style={{ fontSize: '11px', color: '#555' }}>
          Ask a question to start a conversation.
        </span>
      </div>
    );
  }

  const toggleCitations = (index: number) => {
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

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedId(index);
      setTimeout(() => setCopiedId(null), 1500);
    });
  };

  const generateSuggestions = (item: QAHistory): string[] => {
    const keywords = item.question.toLowerCase().split(/\s+/).filter(w => w.length > 3);
    const suggestions: string[] = [];

    if (keywords.some(k => k.includes('design') || k.includes('architecture'))) {
      suggestions.push('What design patterns are used in the services layer?');
      suggestions.push('How does the preload bridge ensure security?');
    } else if (keywords.some(k => k.includes('import') || k.includes('document'))) {
      suggestions.push('What file formats are supported for import?');
      suggestions.push('How are imported documents stored?');
    } else if (keywords.some(k => k.includes('index') || k.includes('chunk'))) {
      suggestions.push('What is the chunk size used for indexing?');
      suggestions.push('How does keyword matching rank chunks?');
    } else {
      suggestions.push('Tell me more about the document indexing process');
      suggestions.push('What documents are available for search?');
    }

    return suggestions.slice(0, 2);
  };

  return (
    <div style={{ flex: 1, overflow: 'auto', padding: '8px' }}>
      {history.map((item, i) => {
        const time = new Date(item.response.timestamp);
        const timeStr = time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const dateStr = time.toLocaleDateString([], { month: 'short', day: 'numeric' });
        const isExpanded = expandedCitations.has(i);
        const isCopied = copiedId === i;

        return (
          <div key={i} style={{ marginBottom: '12px' }}>
            {/* Date separator for first item or new date */}
            {(i === 0 || dateStr !== new Date(history[i - 1].response.timestamp).toLocaleDateString([], { month: 'short', day: 'numeric' })) && (
              <div style={{
                textAlign: 'center',
                fontSize: '10px',
                color: '#555',
                margin: '8px 0',
                position: 'relative',
              }}>
                <span style={{
                  background: '#16213e',
                  padding: '0 8px',
                  position: 'relative',
                  zIndex: 1,
                }}>
                  {dateStr}
                </span>
                <div style={{
                  position: 'absolute',
                  top: '50%',
                  left: '0',
                  right: '0',
                  height: '1px',
                  background: '#0f3460',
                }} />
              </div>
            )}

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
                padding: '10px 12px',
                background: '#1a1a3e',
                color: '#e0e0e0',
                borderRadius: '12px 12px 12px 2px',
                fontSize: '11px',
                lineHeight: 1.5,
              }}>
                {item.response.answer}

                {/* Citation section */}
                {item.response.citations.length > 0 && (
                  <div style={{ marginTop: '8px' }}>
                    <button
                      onClick={() => toggleCitations(i)}
                      style={{
                        fontSize: '10px',
                        color: '#8888bb',
                        background: 'none',
                        border: 'none',
                        cursor: 'pointer',
                        padding: '2px 0',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                      }}
                    >
                      <span style={{ transform: isExpanded ? 'rotate(90deg)' : 'rotate(0)', transition: 'transform 0.15s', display: 'inline-block' }}>&#9654;</span>
                      {item.response.citations.length} citation(s)
                    </button>

                    {isExpanded && (
                      <div style={{ marginTop: '4px' }}>
                        {item.response.citations.map((c: Citation, ci: number) => (
                          <div key={ci} style={{
                            fontSize: '10px',
                            color: '#888',
                            padding: '4px 8px',
                            marginTop: '2px',
                            borderLeft: '2px solid #533483',
                            background: '#161636',
                            borderRadius: '0 4px 4px 0',
                          }}>
                            <span style={{ color: '#a0a0c0', fontWeight: 500 }}>{c.documentTitle}</span>
                            <span style={{ color: '#666' }}> (chunk {c.chunkIndex})</span>
                            <br />
                            {c.excerpt.substring(0, 120)}...
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Action row */}
                <div style={{
                  display: 'flex',
                  gap: '8px',
                  marginTop: '6px',
                  borderTop: '1px solid #0f3460',
                  paddingTop: '4px',
                }}>
                  <button
                    onClick={() => copyToClipboard(item.response.answer, i)}
                    style={{
                      fontSize: '10px',
                      color: '#888',
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      padding: '2px 4px',
                    }}
                  >
                    {isCopied ? 'Copied!' : 'Copy'}
                  </button>
                  <span style={{ fontSize: '10px', color: '#666' }}>
                    Confidence: {Math.round(item.response.confidence * 100)}%
                  </span>
                </div>
              </div>
            </div>

            {/* Timestamp */}
            <div style={{
              fontSize: '10px',
              color: '#555',
              textAlign: 'center',
              padding: '0 4px',
              marginBottom: '4px',
            }}>
              {timeStr}
            </div>

            {/* Follow-up suggestions */}
            {onFollowUp && i === history.length - 1 && (
              <div style={{ padding: '4px 8px' }}>
                <div style={{ fontSize: '10px', color: '#555', marginBottom: '4px' }}>
                  Suggested follow-ups:
                </div>
                {generateSuggestions(item).map((suggestion, si) => (
                  <button
                    key={si}
                    onClick={() => onFollowUp(suggestion)}
                    style={{
                      display: 'block',
                      width: '100%',
                      textAlign: 'left',
                      fontSize: '11px',
                      color: '#a0a0c0',
                      background: '#1a1a2e',
                      border: '1px solid #0f3460',
                      borderRadius: '4px',
                      padding: '6px 8px',
                      marginBottom: '4px',
                      cursor: 'pointer',
                    }}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
