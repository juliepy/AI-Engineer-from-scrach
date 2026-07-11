import { IpcMain } from 'electron';
import { DocumentService } from '../services/document-service';
import { IndexingService } from '../services/indexing-service';
import { QaService } from '../services/qa-service';
import { IPC_CHANNELS } from '../shared/types';
import { logger } from '../services/logger';

export interface Services {
  documentService: DocumentService;
  indexingService: IndexingService;
  qaService: QaService;
}

export function registerIpcHandlers(ipcMain: IpcMain, services: Services) {
  const { documentService, indexingService, qaService } = services;
  const log = logger.forService('IPC');

  // Document operations
  ipcMain.handle(IPC_CHANNELS.LIST_DOCUMENTS, async () => {
    log.info('LIST_DOCUMENTS');
    return documentService.listDocuments();
  });

  ipcMain.handle(IPC_CHANNELS.IMPORT_DOCUMENT, async (_event, filePath: string) => {
    log.info('IMPORT_DOCUMENT', { filePath });
    try {
      const doc = documentService.importDocument(filePath);
      log.info('Document imported', { id: doc.id, title: doc.title, size: doc.size });
      return doc;
    } catch (err) {
      log.error('Document import failed', { filePath, error: String(err) });
      throw err;
    }
  });

  ipcMain.handle(IPC_CHANNELS.GET_DOCUMENT, async (_event, id: string) => {
    log.info('GET_DOCUMENT', { id });
    return documentService.getDocument(id);
  });

  ipcMain.handle(IPC_CHANNELS.DELETE_DOCUMENT, async (_event, id: string) => {
    log.info('DELETE_DOCUMENT', { id });
    return documentService.deleteDocument(id);
  });

  // Indexing
  ipcMain.handle(IPC_CHANNELS.START_INDEXING, async (_event, documentId?: string) => {
    log.info('START_INDEXING', { documentId: documentId ?? 'all' });
    try {
      const status = await indexingService.startIndexing(documentId);
      log.info('Indexing complete', { status: status.status, indexed: status.currentIndexed, total: status.totalDocuments });
      return status;
    } catch (err) {
      log.error('Indexing failed', { documentId, error: String(err) });
      throw err;
    }
  });

  ipcMain.handle(IPC_CHANNELS.GET_INDEXING_STATUS, async () => {
    return indexingService.getStatus();
  });

  ipcMain.handle(IPC_CHANNELS.GET_CHUNKS, async (_event, documentId: string) => {
    log.info('GET_CHUNKS', { documentId });
    return indexingService.getChunksForDocument(documentId);
  });

  // Q&A
  ipcMain.handle(IPC_CHANNELS.ASK_QUESTION, async (_event, question: string) => {
    log.info('ASK_QUESTION', { question });
    try {
      const response = await qaService.ask(question);
      log.info('Q&A response', {
        confidence: response.confidence,
        citationCount: response.citations.length,
      });
      return response;
    } catch (err) {
      log.error('Q&A failed', { question, error: String(err) });
      throw err;
    }
  });

  ipcMain.handle(IPC_CHANNELS.GET_HISTORY, async () => {
    log.info('GET_HISTORY');
    return qaService.getHistory();
  });

  ipcMain.handle(IPC_CHANNELS.CLEAR_HISTORY, async () => {
    log.info('CLEAR_HISTORY');
    qaService.clearHistory();
  });

  // Conversation
  ipcMain.handle(IPC_CHANNELS.GET_CONVERSATION, async () => {
    log.info('GET_CONVERSATION');
    return qaService.getHistory();
  });
}
