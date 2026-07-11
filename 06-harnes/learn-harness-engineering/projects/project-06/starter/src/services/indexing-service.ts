import { v4 as uuidv4 } from 'uuid';
import { Chunk, Document } from '../shared/types';
import { PersistenceService } from './persistence-service';
import { logger } from './logger';

const SERVICE = 'indexing-service';
const INDEX_META = 'index-meta.json';
const CHUNKS_DIR = 'chunks';

interface IndexStatus {
  status: 'idle' | 'indexing' | 'ready' | 'error';
  currentIndexed: number;
  totalDocuments: number;
  lastIndexed: string | null;
}

export class IndexingService {
  private persistence: PersistenceService;

  constructor(persistence: PersistenceService) {
    this.persistence = persistence;
  }

  /** Start indexing documents. If documentId is provided, index only that document. */
  async startIndexing(documentId?: string): Promise<IndexStatus> {
    const status = this.getStatus();

    if (documentId) {
      const content = this.persistence.readText(`content/${documentId}.txt`);
      if (!content) {
        logger.error(SERVICE, `Content not found for document: ${documentId}`);
        return { ...status, status: 'error' };
      }
      const chunks = this.chunkDocument(documentId, content);
      this.persistence.writeJson(`${CHUNKS_DIR}/${documentId}.json`, chunks);
      logger.info(SERVICE, 'Single document indexed', {
        documentId,
        chunkCount: chunks.length,
      });
      return this.getStatus();
    }

    const docsMeta = this.persistence.readJson<Document[]>('documents-meta.json') ?? [];
    const chunksMeta = this.persistence.readJson<Record<string, string[]>>(INDEX_META) ?? {};

    let indexedCount = 0;
    for (const doc of docsMeta) {
      if (chunksMeta[doc.id]) continue;

      const content = this.persistence.readText(`content/${doc.id}.txt`);
      if (!content) continue;

      const chunks = this.chunkDocument(doc.id, content);
      this.persistence.writeJson(`${CHUNKS_DIR}/${doc.id}.json`, chunks);
      chunksMeta[doc.id] = chunks.map(c => c.id);
      indexedCount++;
      logger.info(SERVICE, 'Document indexed', {
        documentId: doc.id,
        chunkCount: chunks.length,
      });
    }

    this.persistence.writeJson(INDEX_META, chunksMeta);
    logger.info(SERVICE, 'Batch indexing complete', {
      totalDocs: docsMeta.length,
      newlyIndexed: indexedCount,
    });
    return this.getStatus();
  }

  /** Get current indexing status. */
  getStatus(): IndexStatus {
    const docs = this.persistence.readJson<Document[]>('documents-meta.json') ?? [];
    const chunksMeta = this.persistence.readJson<Record<string, string[]>>(INDEX_META) ?? {};

    const currentIndexed = Object.keys(chunksMeta).length;
    const totalDocuments = docs.length;
    const isReady = currentIndexed === totalDocuments && totalDocuments > 0;

    return {
      status: isReady ? 'ready' : currentIndexed > 0 ? 'indexing' : 'idle',
      currentIndexed,
      totalDocuments,
      lastIndexed: new Date().toISOString(),
    };
  }

  /** Get all chunks for a document. */
  getChunksForDocument(documentId: string): Chunk[] {
    return this.persistence.readJson<Chunk[]>(`${CHUNKS_DIR}/${documentId}.json`) ?? [];
  }

  /** Get all chunks across all documents. */
  getAllChunks(): Chunk[] {
    const chunksMeta = this.persistence.readJson<Record<string, string[]>>(INDEX_META) ?? {};
    const allChunks: Chunk[] = [];

    for (const docId of Object.keys(chunksMeta)) {
      const chunks = this.getChunksForDocument(docId);
      allChunks.push(...chunks);
    }

    return allChunks;
  }

  /** Split a document into chunks of ~500 characters at paragraph boundaries. */
  private chunkDocument(documentId: string, content: string): Chunk[] {
    const CHUNK_SIZE = 500;
    const chunks: Chunk[] = [];

    const paragraphs = content.split(/\n\s*\n/).filter(p => p.trim().length > 0);

    let buffer = '';
    let chunkIndex = 0;

    for (const para of paragraphs) {
      if (buffer.length + para.length > CHUNK_SIZE && buffer.length > 0) {
        chunks.push(this.createChunk(documentId, chunkIndex++, buffer.trim()));
        buffer = para;
      } else {
        buffer += (buffer ? '\n\n' : '') + para;
      }
    }

    if (buffer.trim()) {
      chunks.push(this.createChunk(documentId, chunkIndex, buffer.trim()));
    }

    return chunks;
  }

  private createChunk(documentId: string, index: number, content: string): Chunk {
    return {
      id: uuidv4(),
      documentId,
      content,
      index,
      metadata: {
        charCount: String(content.length),
        wordCount: String(content.split(/\s+/).length),
      },
    };
  }
}
