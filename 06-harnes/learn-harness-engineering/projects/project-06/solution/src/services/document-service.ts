import * as fs from 'fs';
import * as path from 'path';
import { v4 as uuidv4 } from 'uuid';
import { Document } from '../shared/types';
import { PersistenceService } from './persistence-service';
import { logger } from './logger';

const SERVICE = 'document-service';
const DOCUMENTS_META = 'documents-meta.json';

export class DocumentService {
  private persistence: PersistenceService;
  private log = logger.forService(SERVICE);

  constructor(persistence: PersistenceService) {
    this.persistence = persistence;
    this.log.info('DocumentService initialized');
  }

  /** List all imported documents. */
  listDocuments(): Document[] {
    const docs = this.persistence.readJson<Document[]>(DOCUMENTS_META);
    const count = docs?.length ?? 0;
    this.log.debug('Listing documents', { count });
    return docs ?? [];
  }

  /** Import a file from the given path. */
  importDocument(filePath: string): Document {
    this.log.info('Starting document import', { filePath });

    if (!fs.existsSync(filePath)) {
      this.log.error('File not found during import', { filePath });
      throw new Error(`File not found: ${filePath}`);
    }

    const filename = path.basename(filePath);
    const content = fs.readFileSync(filePath, 'utf-8');
    const stats = fs.statSync(filePath);

    if (stats.size > 10 * 1024 * 1024) {
      this.log.error('File exceeds 10MB size limit', { filePath, sizeBytes: stats.size });
      throw new Error(`File too large: ${filename} (${(stats.size / 1024 / 1024).toFixed(1)} MB). Maximum size is 10 MB.`);
    }

    const doc: Document = {
      id: uuidv4(),
      title: filename.replace(/\.[^.]+$/, ''),
      filename,
      importedAt: new Date().toISOString(),
      size: stats.size,
      status: 'imported',
    };

    // Copy file to data directory
    this.persistence.copyFileToDocuments(filePath, filename);

    // Store content for indexing
    this.persistence.writeText(`content/${doc.id}.txt`, content);

    // Update metadata
    const docs = this.listDocuments();
    docs.push(doc);
    this.persistence.writeJson(DOCUMENTS_META, docs);

    this.log.info('Document imported successfully', {
      documentId: doc.id,
      filename: doc.filename,
      sizeBytes: doc.size,
      contentLength: content.length,
      totalDocuments: docs.length,
    });
    return doc;
  }

  /** Get a single document by ID. */
  getDocument(id: string): Document | null {
    const docs = this.listDocuments();
    const doc = docs.find(d => d.id === id) ?? null;
    if (!doc) {
      this.log.warn('Document not found', { documentId: id });
    }
    return doc;
  }

  /** Get the text content of a document. */
  getDocumentContent(id: string): string | null {
    const content = this.persistence.readText(`content/${id}.txt`);
    if (!content) {
      this.log.warn('Document content not found', { documentId: id });
    }
    return content;
  }

  /** Update a document's metadata. */
  updateDocument(id: string, updates: Partial<Document>): Document | null {
    const docs = this.listDocuments();
    const index = docs.findIndex(d => d.id === id);
    if (index === -1) {
      this.log.warn('Cannot update -- document not found', { documentId: id });
      return null;
    }

    docs[index] = { ...docs[index], ...updates };
    this.persistence.writeJson(DOCUMENTS_META, docs);
    this.log.info('Document metadata updated', {
      documentId: id,
      updatedFields: Object.keys(updates),
    });
    return docs[index];
  }

  /** Delete a document by ID. */
  deleteDocument(id: string): boolean {
    const docs = this.listDocuments();
    const doc = docs.find(d => d.id === id);
    if (!doc) {
      this.log.warn('Cannot delete -- document not found', { documentId: id });
      return false;
    }

    this.persistence.deleteFromDocuments(doc.filename);
    // Also remove content file
    const contentPath = `content/${id}.txt`;
    if (this.persistence.exists(contentPath)) {
      this.persistence.writeText(contentPath, ''); // Clear content
    }

    const updated = docs.filter(d => d.id !== id);
    this.persistence.writeJson(DOCUMENTS_META, updated);

    this.log.info('Document deleted', {
      documentId: id,
      filename: doc.filename,
      remainingDocuments: updated.length,
    });
    return true;
  }

  /** Check if any data has been persisted. */
  hasPersistedData(): boolean {
    return this.persistence.exists(DOCUMENTS_META);
  }
}
