import { IpcMain } from 'electron';
import { DocumentService } from '../services/document-service';
import { IndexingService } from '../services/indexing-service';
import { QaService } from '../services/qa-service';
import { PersistenceService } from '../services/persistence-service';
import { IPC_CHANNELS } from '../shared/types';
import { logger } from '../services/logger';

const SERVICE = 'ipc-handlers';

export interface Services {
  documentService: DocumentService;
  indexingService: IndexingService;
  qaService: QaService;
  persistence: PersistenceService;
}

export function registerIpcHandlers(ipcMain: IpcMain, services: Services) {
  const { documentService, indexingService, qaService, persistence } = services;

  // ---- Document operations ----

  ipcMain.handle(IPC_CHANNELS.LIST_DOCUMENTS, async () => {
    logger.debug(SERVICE, 'IPC: LIST_DOCUMENTS');
    return documentService.listDocuments();
  });

  ipcMain.handle(IPC_CHANNELS.IMPORT_DOCUMENT, async (_event, filePath: string) => {
    logger.info(SERVICE, 'IPC: IMPORT_DOCUMENT', { filePath });
    return documentService.importDocument(filePath);
  });

  ipcMain.handle(IPC_CHANNELS.GET_DOCUMENT, async (_event, id: string) => {
    logger.debug(SERVICE, 'IPC: GET_DOCUMENT', { id });
    return documentService.getDocument(id);
  });

  ipcMain.handle(IPC_CHANNELS.DELETE_DOCUMENT, async (_event, id: string) => {
    logger.info(SERVICE, 'IPC: DELETE_DOCUMENT', { id });
    return documentService.deleteDocument(id);
  });

  // ---- Indexing ----

  ipcMain.handle(IPC_CHANNELS.START_INDEXING, async (_event, documentId?: string) => {
    logger.info(SERVICE, 'IPC: START_INDEXING', { documentId: documentId ?? 'all' });
    return indexingService.startIndexing(documentId);
  });

  ipcMain.handle(IPC_CHANNELS.GET_INDEXING_STATUS, async () => {
    logger.debug(SERVICE, 'IPC: GET_INDEXING_STATUS');
    return indexingService.getStatus();
  });

  ipcMain.handle(IPC_CHANNELS.GET_CHUNKS, async (_event, documentId: string) => {
    logger.debug(SERVICE, 'IPC: GET_CHUNKS', { documentId });
    return indexingService.getChunksForDocument(documentId);
  });

  // ---- Q&A ----

  ipcMain.handle(IPC_CHANNELS.ASK_QUESTION, async (_event, question: string) => {
    logger.info(SERVICE, 'IPC: ASK_QUESTION', { question });
    return qaService.ask(question);
  });

  ipcMain.handle(IPC_CHANNELS.GET_HISTORY, async () => {
    logger.debug(SERVICE, 'IPC: GET_HISTORY');
    return qaService.getHistory();
  });

  ipcMain.handle(IPC_CHANNELS.CLEAR_HISTORY, async () => {
    logger.info(SERVICE, 'IPC: CLEAR_HISTORY');
    return qaService.clearHistory();
  });

  // ---- Feedback ----

  ipcMain.handle(IPC_CHANNELS.SUBMIT_FEEDBACK, async (_event, qaTimestamp: string, question: string, rating: 'positive' | 'negative', comment?: string) => {
    logger.info(SERVICE, 'IPC: SUBMIT_FEEDBACK', { qaTimestamp, rating });
    return qaService.submitFeedback(qaTimestamp, question, rating, comment ?? '');
  });

  ipcMain.handle(IPC_CHANNELS.GET_FEEDBACK, async () => {
    logger.debug(SERVICE, 'IPC: GET_FEEDBACK');
    return qaService.getFeedback();
  });

  // ---- Clean state ----

  ipcMain.handle(IPC_CHANNELS.RESET_DATA, async () => {
    logger.warn(SERVICE, 'IPC: RESET_DATA -- resetting all application data');
    persistence.resetAll();
    return { success: true };
  });

  // ---- App status ----

  ipcMain.handle(IPC_CHANNELS.GET_STATUS, async () => {
    logger.debug(SERVICE, 'IPC: GET_STATUS');
    return indexingService.getStatus();
  });

  logger.info(SERVICE, 'All IPC handlers registered', {
    channels: Object.values(IPC_CHANNELS).length,
  });
}
