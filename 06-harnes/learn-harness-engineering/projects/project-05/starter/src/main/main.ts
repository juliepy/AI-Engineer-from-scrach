import { app, BrowserWindow, ipcMain } from 'electron';
import * as path from 'path';
import { registerIpcHandlers } from './ipc-handlers';
import { DocumentService } from '../services/document-service';
import { QaService } from '../services/qa-service';
import { IndexingService } from '../services/indexing-service';
import { PersistenceService } from '../services/persistence-service';
import { logger } from '../services/logger';

let mainWindow: BrowserWindow | null = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, '..', 'preload', 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
    title: 'Knowledge Base',
  });

  // In development, load from Vite dev server or built renderer
  const isDev = !app.isPackaged;
  if (isDev) {
    mainWindow.loadFile(path.join(__dirname, '..', 'renderer', 'index.html'));
  } else {
    mainWindow.loadFile(path.join(__dirname, '..', 'renderer', 'index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function initializeServices() {
  const log = logger.forService('App');

  log.info('Starting service initialization');
  const dataDir = path.join(app.getPath('userData'), 'knowledge-base-data');
  log.info('Data directory resolved', { dataDir });

  const persistence = new PersistenceService(dataDir);
  log.info('PersistenceService initialized');

  const documentService = new DocumentService(persistence);
  log.info('DocumentService initialized');

  const indexingService = new IndexingService(persistence);
  log.info('IndexingService initialized');

  const qaService = new QaService(persistence, indexingService);
  log.info('QaService initialized');

  registerIpcHandlers(ipcMain, {
    documentService,
    indexingService,
    qaService,
  });

  log.info('All services initialized and IPC handlers registered');
}

app.whenReady().then(() => {
  const log = logger.forService('App');
  log.info('Electron app ready, initializing...');

  initializeServices();
  createWindow();

  log.info('Application startup complete');

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  const log = logger.forService('App');
  log.info('All windows closed');
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
