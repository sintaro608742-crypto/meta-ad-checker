// ============================================
// Logger Utility - 開発環境専用ロギング
// 本番環境では自動的に無効化される
// ============================================

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogContext {
  [key: string]: unknown;
}

class Logger {
  private isDevelopment = import.meta.env.MODE === 'development';

  private log(level: LogLevel, message: string, context?: LogContext): void {
    if (!this.isDevelopment) return;

    const timestamp = new Date().toISOString();
    const contextStr = context ? ` | ${JSON.stringify(context)}` : '';

    switch (level) {
      case 'debug':
        // eslint-disable-next-line no-console
        console.log(`[${timestamp}] DEBUG: ${message}${contextStr}`);
        break;
      case 'info':
        // eslint-disable-next-line no-console
        console.info(`[${timestamp}] INFO: ${message}${contextStr}`);
        break;
      case 'warn':
        // eslint-disable-next-line no-console
        console.warn(`[${timestamp}] WARN: ${message}${contextStr}`);
        break;
      case 'error':
        // eslint-disable-next-line no-console
        console.error(`[${timestamp}] ERROR: ${message}${contextStr}`);
        break;
    }
  }

  debug(message: string, context?: LogContext): void {
    this.log('debug', message, context);
  }

  info(message: string, context?: LogContext): void {
    this.log('info', message, context);
  }

  warn(message: string, context?: LogContext): void {
    this.log('warn', message, context);
  }

  error(message: string, context?: LogContext): void {
    this.log('error', message, context);
  }
}

export const logger = new Logger();
