/**
 * Structured logging module for the Knowledge Base application.
 *
 * Provides log levels, timestamps, and structured JSON output for
 * all services. Replaces raw console.log calls with consistent,
 * machine-parseable log entries.
 *
 * Usage:
 *   import { logger } from './logger';
 *   const log = logger.forService('my-service');
 *   log.info('Operation completed', { documentId: 'abc123', duration: 42 });
 *
 * Output:
 *   {"timestamp":"2026-03-30T12:00:00.000Z","level":"INFO","service":"my-service","message":"Operation completed","data":{"documentId":"abc123","duration":42}}
 */

export enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARN = 'WARN',
  ERROR = 'ERROR',
}

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  service: string;
  message: string;
  data?: Record<string, unknown>;
}

class Logger {
  private minLevel: LogLevel;
  private static readonly LEVEL_ORDER: LogLevel[] = [
    LogLevel.DEBUG,
    LogLevel.INFO,
    LogLevel.WARN,
    LogLevel.ERROR,
  ];

  constructor(minLevel: LogLevel = LogLevel.DEBUG) {
    this.minLevel = minLevel;
  }

  private shouldLog(level: LogLevel): boolean {
    const minIdx = Logger.LEVEL_ORDER.indexOf(this.minLevel);
    const levelIdx = Logger.LEVEL_ORDER.indexOf(level);
    return levelIdx >= minIdx;
  }

  private emit(entry: LogEntry): void {
    const output = JSON.stringify(entry);
    switch (entry.level) {
      case LogLevel.ERROR:
        console.error(output);
        break;
      case LogLevel.WARN:
        console.warn(output);
        break;
      default:
        console.log(output);
        break;
    }
  }

  private log(level: LogLevel, service: string, message: string, data?: Record<string, unknown>): void {
    if (!this.shouldLog(level)) return;

    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      service,
      message,
    };

    if (data && Object.keys(data).length > 0) {
      entry.data = data;
    }

    this.emit(entry);
  }

  debug(service: string, message: string, data?: Record<string, unknown>): void {
    this.log(LogLevel.DEBUG, service, message, data);
  }

  info(service: string, message: string, data?: Record<string, unknown>): void {
    this.log(LogLevel.INFO, service, message, data);
  }

  warn(service: string, message: string, data?: Record<string, unknown>): void {
    this.log(LogLevel.WARN, service, message, data);
  }

  error(service: string, message: string, data?: Record<string, unknown>): void {
    this.log(LogLevel.ERROR, service, message, data);
  }

  /** Create a child logger scoped to a specific service. */
  forService(serviceName: string): ServiceLogger {
    return new ServiceLogger(this, serviceName);
  }
}

class ServiceLogger {
  private logger: Logger;
  private serviceName: string;

  constructor(logger: Logger, serviceName: string) {
    this.logger = logger;
    this.serviceName = serviceName;
  }

  debug(message: string, data?: Record<string, unknown>): void {
    this.logger.debug(this.serviceName, message, data);
  }

  info(message: string, data?: Record<string, unknown>): void {
    this.logger.info(this.serviceName, message, data);
  }

  warn(message: string, data?: Record<string, unknown>): void {
    this.logger.warn(this.serviceName, message, data);
  }

  error(message: string, data?: Record<string, unknown>): void {
    this.logger.error(this.serviceName, message, data);
  }
}

/** Singleton logger instance for the application. */
export const logger = new Logger(
  (process.env.LOG_LEVEL as LogLevel) ?? LogLevel.DEBUG
);

export { ServiceLogger };
