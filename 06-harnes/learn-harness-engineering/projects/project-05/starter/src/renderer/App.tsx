import React, { useState, useCallback, useEffect } from 'react';
import { DocumentList } from './components/DocumentList';
import { QuestionPanel } from './components/QuestionPanel';
import { DocumentDetail } from './components/DocumentDetail';
import { ConversationHistory } from './components/ConversationHistory';
import { StatusBar } from './components/StatusBar';
import { Document, AppStatus, QAResponse, QAHistory } from '../../shared/types';

declare global {
  interface Window {
    knowledgeBase: {
      documents: {
        list: () => Promise<Document[]>;
        import: (filePath: string) => Promise<Document>;
        get: (id: string) => Promise<Document | null>;
        delete: (id: string) => Promise<boolean>;
      };
      indexing: {
        start: (documentId?: string) => Promise<{ status: string }>;
        status: () => Promise<AppStatus>;
        chunks: (documentId: string) => Promise<Array<{ id: string; content: string; index: number }>>;
      };
      qa: {
        ask: (question: string) => Promise<QAResponse>;
        history: () => Promise<QAHistory[]>;
        clearHistory: () => Promise<void>;
      };
      conversation: {
        get: () => Promise<QAHistory[]>;
      };
    };
  }
}

export function App() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
  const [appStatus, setAppStatus] = useState<AppStatus>({
    documentsLoaded: 0,
    indexStatus: 'idle',
    lastActivity: '',
  });
  const [lastResponse, setLastResponse] = useState<QAResponse | null>(null);
  const [conversationHistory, setConversationHistory] = useState<QAHistory[]>([]);
  const [activeTab, setActiveTab] = useState<'documents' | 'conversation'>('documents');

  const refreshDocuments = useCallback(async () => {
    try {
      const docs = await window.knowledgeBase.documents.list();
      setDocuments(docs);
      const status = await window.knowledgeBase.indexing.status();
      setAppStatus(status);
    } catch (err) {
      console.error('Failed to refresh documents:', err);
    }
  }, []);

  const refreshHistory = useCallback(async () => {
    try {
      const history = await window.knowledgeBase.conversation.get();
      setConversationHistory(history);
    } catch (err) {
      console.error('Failed to refresh conversation history:', err);
    }
  }, []);

  useEffect(() => {
    refreshDocuments();
    refreshHistory();
  }, [refreshDocuments, refreshHistory]);

  const handleImport = useCallback(async () => {
    console.log('Import triggered - use window.knowledgeBase.documents.import(filePath)');
  }, []);

  const handleSelectDocument = useCallback((doc: Document) => {
    setSelectedDoc(doc);
  }, []);

  const handleAskQuestion = useCallback(async (question: string) => {
    try {
      const response = await window.knowledgeBase.qa.ask(question);
      setLastResponse(response);
      refreshHistory();
    } catch (err) {
      console.error('Q&A failed:', err);
    }
  }, [refreshHistory]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <header style={{
        padding: '12px 20px',
        background: '#16213e',
        borderBottom: '1px solid #0f3460',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <h1 style={{ fontSize: '18px', fontWeight: 600 }}>Knowledge Base</h1>
        <button
          onClick={refreshDocuments}
          style={{
            padding: '6px 14px',
            background: '#0f3460',
            color: '#e0e0e0',
            border: '1px solid #1a1a4e',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '13px',
          }}
        >
          Refresh
        </button>
      </header>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Left panel: Document list + Conversation tabs */}
        <div style={{
          width: '280px',
          borderRight: '1px solid #0f3460',
          display: 'flex',
          flexDirection: 'column',
          background: '#16213e',
        }}>
          <div style={{
            display: 'flex',
            borderBottom: '1px solid #0f3460',
          }}>
            <button
              onClick={() => setActiveTab('documents')}
              style={{
                flex: 1,
                padding: '8px',
                background: activeTab === 'documents' ? '#0f3460' : 'transparent',
                color: activeTab === 'documents' ? '#e0e0e0' : '#666',
                border: 'none',
                borderBottom: activeTab === 'documents' ? '2px solid #533483' : '2px solid transparent',
                cursor: 'pointer',
                fontSize: '12px',
                fontWeight: 500,
              }}
            >
              Documents ({documents.length})
            </button>
            <button
              onClick={() => setActiveTab('conversation')}
              style={{
                flex: 1,
                padding: '8px',
                background: activeTab === 'conversation' ? '#0f3460' : 'transparent',
                color: activeTab === 'conversation' ? '#e0e0e0' : '#666',
                border: 'none',
                borderBottom: activeTab === 'conversation' ? '2px solid #533483' : '2px solid transparent',
                cursor: 'pointer',
                fontSize: '12px',
                fontWeight: 500,
              }}
            >
              History ({conversationHistory.length})
            </button>
          </div>
          {activeTab === 'documents' ? (
            <>
              <div style={{
                padding: '6px 16px',
                display: 'flex',
                justifyContent: 'flex-end',
              }}>
                <button
                  onClick={handleImport}
                  style={{
                    padding: '4px 10px',
                    background: '#533483',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '3px',
                    cursor: 'pointer',
                    fontSize: '12px',
                  }}
                >
                  + Import
                </button>
              </div>
              <DocumentList
                documents={documents}
                onSelect={handleSelectDocument}
                selectedId={selectedDoc?.id ?? null}
              />
            </>
          ) : (
            <ConversationHistory history={conversationHistory} />
          )}
        </div>

        {/* Right panel: Document detail + Q&A */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <div style={{ flex: 1, overflow: 'auto', padding: '20px' }}>
            {selectedDoc ? (
              <DocumentDetail document={selectedDoc} />
            ) : (
              <div style={{ color: '#666', textAlign: 'center', paddingTop: '40px' }}>
                Select a document or ask a question to get started
              </div>
            )}
            {lastResponse && (
              <div style={{
                marginTop: '16px',
                padding: '16px',
                background: '#1a1a3e',
                borderRadius: '6px',
                border: '1px solid #0f3460',
              }}>
                <div style={{ fontSize: '14px', lineHeight: 1.6 }}>{lastResponse.answer}</div>
                {lastResponse.citations.length > 0 && (
                  <div style={{ marginTop: '10px', fontSize: '12px', color: '#8888bb' }}>
                    <strong>Citations:</strong>
                    {lastResponse.citations.map((c, i) => (
                      <div key={i} style={{ marginTop: '4px', paddingLeft: '8px', borderLeft: '2px solid #533483' }}>
                        {c.documentTitle} (chunk {c.chunkIndex}): {c.excerpt.substring(0, 100)}...
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          <QuestionPanel onAsk={handleAskQuestion} />
        </div>
      </div>

      <StatusBar status={appStatus} />
    </div>
  );
}
