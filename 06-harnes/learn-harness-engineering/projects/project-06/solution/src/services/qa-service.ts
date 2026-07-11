import { v4 as uuidv4 } from 'uuid';
import { QAResponse, QAHistory, Citation, FeedbackEntry } from '../shared/types';
import { PersistenceService } from './persistence-service';
import { IndexingService } from './indexing-service';
import { logger } from './logger';

const SERVICE = 'qa-service';
const QA_HISTORY_FILE = 'qa-history.json';
const FEEDBACK_FILE = 'feedback.json';

/** Mock Q&A patterns keyed to document content keywords. */
const MOCK_PATTERNS: Array<{
  keywords: string[];
  answer: string;
  excerpt: string;
}> = [
  {
    keywords: ['design', 'architecture', 'pattern'],
    answer: 'The system uses a layered architecture with clear boundaries between the main process, preload scripts, and renderer. Each layer communicates through typed IPC channels, and the services layer handles business logic independently of the UI.',
    excerpt: 'The system uses a layered architecture with clear boundaries',
  },
  {
    keywords: ['import', 'document', 'file'],
    answer: 'Documents are imported by copying the source file to the local data directory. The system extracts text content and creates metadata including title, filename, size, and import timestamp. After import, documents can be indexed for search.',
    excerpt: 'Documents are imported by copying the source file',
  },
  {
    keywords: ['index', 'chunk', 'search'],
    answer: 'The indexing pipeline splits documents into chunks of approximately 500 characters at paragraph boundaries. Each chunk includes metadata like character count and word count. The index enables grounded Q&A with citations pointing to specific document sections.',
    excerpt: 'The indexing pipeline splits documents into chunks',
  },
  {
    keywords: ['retrieval', 'search', 'query'],
    answer: 'Retrieval works by matching query keywords against indexed chunks. The system ranks chunks by keyword overlap and returns the most relevant excerpts as citations alongside the generated answer.',
    excerpt: 'Retrieval works by matching query keywords against indexed chunks',
  },
  {
    keywords: ['meeting', 'notes', 'summary'],
    answer: 'The meeting summary indicates that the team discussed implementing a retrieval-augmented generation pipeline. Key decisions included using local chunk storage and citation-based verification to ensure answer accuracy.',
    excerpt: 'The team discussed implementing a retrieval-augmented generation pipeline',
  },
  {
    keywords: ['logging', 'debug', 'observe', 'monitor'],
    answer: 'The application uses structured JSON logging throughout all services. Each log entry includes a timestamp, log level, service name, and optional data payload. This enables runtime observability and debugging of the full document lifecycle.',
    excerpt: 'The application uses structured JSON logging throughout all services',
  },
  {
    keywords: ['feedback', 'rating', 'quality'],
    answer: 'Users can provide positive or negative feedback on Q&A responses. Feedback is stored alongside the question and answer in a dedicated feedback log. This data can be used to improve answer quality over time.',
    excerpt: 'Users can provide positive or negative feedback on Q&A responses',
  },
  {
    keywords: ['clean', 'reset', 'benchmark'],
    answer: 'The application supports resetting all data to a clean state. This clears documents, chunks, Q&A history, and feedback data. It is useful for testing and benchmarking the full pipeline from scratch.',
    excerpt: 'The application supports resetting all data to a clean state',
  },
];

/** Generate follow-up suggestions based on the answer context. */
function generateFollowUps(question: string, citations: Citation[]): string[] {
  const suggestions: string[] = [];

  if (citations.length > 0) {
    suggestions.push(`Tell me more about ${citations[0].documentTitle}`);
  }

  const questionLower = question.toLowerCase();
  if (questionLower.includes('architecture') || questionLower.includes('design')) {
    suggestions.push('How does the indexing pipeline work?');
    suggestions.push('What logging is available?');
  } else if (questionLower.includes('import') || questionLower.includes('document')) {
    suggestions.push('How are documents indexed?');
    suggestions.push('What file formats are supported?');
  } else if (questionLower.includes('index') || questionLower.includes('chunk')) {
    suggestions.push('How does keyword retrieval work?');
    suggestions.push('What is the chunk size?');
  } else {
    suggestions.push('What is the system architecture?');
    suggestions.push('How do I import documents?');
  }

  return suggestions.slice(0, 3);
}

export class QaService {
  private persistence: PersistenceService;
  private indexingService: IndexingService;
  private log = logger.forService(SERVICE);

  constructor(persistence: PersistenceService, indexingService?: IndexingService) {
    this.persistence = persistence;
    this.indexingService = indexingService ?? new IndexingService(persistence);
    this.log.info('QaService initialized');
  }

  /** Ask a question and get a grounded answer with citations. */
  async ask(question: string): Promise<QAResponse> {
    const startTime = Date.now();
    this.log.info('Processing question', { question, questionLength: question.length });

    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 100 + Math.random() * 400));

    const chunks = this.indexingService.getAllChunks();
    const citations: Citation[] = [];

    if (chunks.length > 0) {
      // Find relevant chunks using keyword matching
      const questionWords = question.toLowerCase().split(/\s+/).filter(w => w.length > 2);
      this.log.debug('Tokenized question', { words: questionWords, chunkPool: chunks.length });

      const scored = chunks.map(chunk => {
        const contentLower = chunk.content.toLowerCase();
        const score = questionWords.reduce(
          (acc, word) => acc + (contentLower.includes(word) ? 1 : 0),
          0
        );
        return { chunk, score };
      });

      // Take top 2 relevant chunks as citations
      const relevant = scored
        .filter(s => s.score > 0)
        .sort((a, b) => b.score - a.score)
        .slice(0, 2);

      // Get document metadata for citations
      const docs = this.persistence.readJson<Array<{ id: string; title: string }>>('documents-meta.json') ?? [];

      for (const { chunk, score } of relevant) {
        const doc = docs.find(d => d.id === chunk.documentId);
        citations.push({
          documentId: chunk.documentId,
          documentTitle: doc?.title ?? 'Unknown Document',
          chunkIndex: chunk.index,
          excerpt: chunk.content.substring(0, 200),
        });
        this.log.debug('Citation matched', {
          documentId: chunk.documentId,
          chunkIndex: chunk.index,
          score,
        });
      }
    } else {
      this.log.warn('No chunks available for retrieval -- index documents first');
    }

    // Generate answer from mock patterns or use fallback
    const answer = this.generateAnswer(question, citations);

    const response: QAResponse = {
      answer,
      citations,
      confidence: citations.length > 0 ? 0.85 : 0.3,
      timestamp: new Date().toISOString(),
    };

    // Save to history
    this.saveToHistory(question, response);

    const duration = Date.now() - startTime;
    this.log.info('Answer generated', {
      confidence: response.confidence,
      citationCount: citations.length,
      answerLength: answer.length,
      durationMs: duration,
    });
    return response;
  }

  /** Get the Q&A history. */
  getHistory(): QAHistory[] {
    const history = this.persistence.readJson<QAHistory[]>(QA_HISTORY_FILE) ?? [];
    this.log.debug('Retrieved Q&A history', { count: history.length });
    return history;
  }

  /** Clear the Q&A history. */
  clearHistory(): void {
    this.persistence.writeJson(QA_HISTORY_FILE, []);
    this.log.info('Q&A history cleared');
  }

  /** Submit feedback for a Q&A response. */
  submitFeedback(qaTimestamp: string, question: string, rating: 'positive' | 'negative', comment: string = ''): FeedbackEntry {
    const entry: FeedbackEntry = {
      id: uuidv4(),
      qaTimestamp,
      question,
      rating,
      comment,
      submittedAt: new Date().toISOString(),
    };

    const feedback = this.getFeedback();
    feedback.push(entry);
    this.persistence.writeJson(FEEDBACK_FILE, feedback);

    this.log.info('Feedback submitted', {
      feedbackId: entry.id,
      rating: entry.rating,
      questionLength: question.length,
    });
    return entry;
  }

  /** Get all feedback entries. */
  getFeedback(): FeedbackEntry[] {
    return this.persistence.readJson<FeedbackEntry[]>(FEEDBACK_FILE) ?? [];
  }

  private generateAnswer(question: string, citations: Citation[]): string {
    // Match against mock patterns
    const questionLower = question.toLowerCase();
    for (const pattern of MOCK_PATTERNS) {
      if (pattern.keywords.some(kw => questionLower.includes(kw))) {
        if (citations.length > 0) {
          return `${pattern.answer} Based on the document "${citations[0].documentTitle}", ${citations[0].excerpt.substring(0, 100)}.`;
        }
        return pattern.answer;
      }
    }

    // Fallback answer
    if (citations.length > 0) {
      return `Based on the available documents, the most relevant information comes from "${citations[0].documentTitle}": ${citations[0].excerpt.substring(0, 150)}. However, a more specific answer would require additional context.`;
    }

    return 'No relevant documents have been indexed yet. Please import and index documents before asking questions.';
  }

  private saveToHistory(question: string, response: QAResponse): void {
    const history = this.getHistory();
    history.push({ question, response });
    this.persistence.writeJson(QA_HISTORY_FILE, history);
  }
}
