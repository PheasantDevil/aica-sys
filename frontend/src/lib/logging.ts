import winston from "winston";
import DailyRotateFile from "winston-daily-rotate-file";

export enum LogLevel {
  ERROR = "error",
  WARN = "warn",
  INFO = "info",
  HTTP = "http",
  VERBOSE = "verbose",
  DEBUG = "debug",
  SILLY = "silly",
}

export interface LogContext {
  userId?: string;
  sessionId?: string;
  requestId?: string;
  component?: string;
  action?: string;
  method?: string;
  url?: string;
  statusCode?: number;
  duration?: number;
  metric?: string;
  value?: number;
  event?: string;
  element?: string;
  errorInfo?: any;
  metadata?: Record<string, any>;
}

export interface LogEntry {
  level: LogLevel;
  message: string;
  context?: LogContext;
  timestamp: Date;
  error?: Error;
}

class Logger {
  private winston: winston.Logger;
  private isDevelopment: boolean;

  constructor() {
    this.isDevelopment = process.env.NODE_ENV === "development";
    this.winston = this.createWinstonLogger();
  }

  private createWinstonLogger(): winston.Logger {
    const transports: winston.transport[] = [];

    // Console transport for development
    if (this.isDevelopment) {
      transports.push(
        new winston.transports.Console({
          format: winston.format.combine(
            winston.format.colorize(),
            winston.format.timestamp(),
            winston.format.printf(({ timestamp, level, message, context, error }: any) => {
              let logMessage = `${timestamp} [${level}]: ${message}`;

              if (context) {
                logMessage += `\nContext: ${JSON.stringify(context, null, 2)}`;
              }

              if (error) {
                const errorMessage = error instanceof Error ? error.stack : String(error);
                logMessage += `\nError: ${errorMessage}`;
              }

              return logMessage;
            }),
          ),
        }),
      );
    }

    // File transports for production
    if (!this.isDevelopment) {
      // Error logs
      transports.push(
        new DailyRotateFile({
          filename: "logs/error-%DATE%.log",
          datePattern: "YYYY-MM-DD",
          level: "error",
          maxSize: "20m",
          maxFiles: "14d",
          format: winston.format.combine(winston.format.timestamp(), winston.format.json()),
        }),
      );

      // Combined logs
      transports.push(
        new DailyRotateFile({
          filename: "logs/combined-%DATE%.log",
          datePattern: "YYYY-MM-DD",
          maxSize: "20m",
          maxFiles: "30d",
          format: winston.format.combine(winston.format.timestamp(), winston.format.json()),
        }),
      );

      // Application logs
      transports.push(
        new DailyRotateFile({
          filename: "logs/app-%DATE%.log",
          datePattern: "YYYY-MM-DD",
          level: "info",
          maxSize: "20m",
          maxFiles: "7d",
          format: winston.format.combine(winston.format.timestamp(), winston.format.json()),
        }),
      );
    }

    return winston.createLogger({
      level: this.isDevelopment ? "debug" : "info",
      transports,
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json(),
      ),
    });
  }

  private log(level: LogLevel, message: string, context?: LogContext, error?: Error): void {
    const logEntry: LogEntry = {
      level,
      message,
      context,
      timestamp: new Date(),
      error,
    };

    this.winston.log(level, message, { context, error });

    // Send to external logging service in production
    if (!this.isDevelopment) {
      this.sendToExternalService(logEntry);
    }
  }

  private async sendToExternalService(logEntry: LogEntry): Promise<void> {
    try {
      // This would integrate with services like DataDog, LogRocket, Sentry, etc.
      if (typeof window !== "undefined" && (window as any).gtag) {
        (window as any).gtag("event", "log", {
          level: logEntry.level,
          message: logEntry.message,
          context: logEntry.context,
        });
      }
    } catch (error) {
      console.error("Failed to send log to external service:", error);
    }
  }

  // Public logging methods
  error(message: string, context?: LogContext, error?: Error): void {
    this.log(LogLevel.ERROR, message, context, error);
  }

  warn(message: string, context?: LogContext): void {
    this.log(LogLevel.WARN, message, context);
  }

  info(message: string, context?: LogContext): void {
    this.log(LogLevel.INFO, message, context);
  }

  http(message: string, context?: LogContext): void {
    this.log(LogLevel.HTTP, message, context);
  }

  verbose(message: string, context?: LogContext): void {
    this.log(LogLevel.VERBOSE, message, context);
  }

  debug(message: string, context?: LogContext): void {
    this.log(LogLevel.DEBUG, message, context);
  }

  silly(message: string, context?: LogContext): void {
    this.log(LogLevel.SILLY, message, context);
  }

  // Specialized logging methods
  userAction(action: string, context?: LogContext): void {
    this.info(`User action: ${action}`, {
      ...context,
      action,
      component: "user-action",
    });
  }

  apiCall(
    method: string,
    url: string,
    statusCode: number,
    duration: number,
    context?: LogContext,
  ): void {
    this.http(`API ${method} ${url} - ${statusCode} (${duration}ms)`, {
      ...context,
      method,
      url,
      statusCode,
      duration,
      component: "api",
    });
  }

  performance(metric: string, value: number, context?: LogContext): void {
    this.info(`Performance: ${metric} = ${value}`, {
      ...context,
      metric,
      value,
      component: "performance",
    });
  }

  security(event: string, context?: LogContext): void {
    this.warn(`Security event: ${event}`, {
      ...context,
      event,
      component: "security",
    });
  }

  business(event: string, context?: LogContext): void {
    this.info(`Business event: ${event}`, {
      ...context,
      event,
      component: "business",
    });
  }
}

// Global logger instance
export const logger = new Logger();

// React hook for logging
export function useLogger() {
  return {
    error: logger.error.bind(logger),
    warn: logger.warn.bind(logger),
    info: logger.info.bind(logger),
    http: logger.http.bind(logger),
    verbose: logger.verbose.bind(logger),
    debug: logger.debug.bind(logger),
    silly: logger.silly.bind(logger),
    userAction: logger.userAction.bind(logger),
    apiCall: logger.apiCall.bind(logger),
    performance: logger.performance.bind(logger),
    security: logger.security.bind(logger),
    business: logger.business.bind(logger),
  };
}

// Error boundary logger
export function logError(error: Error, errorInfo: any, context?: LogContext): void {
  logger.error(
    "React Error Boundary caught an error",
    {
      ...context,
      component: "error-boundary",
      errorInfo,
    },
    error,
  );
}

// Performance monitoring
export function logPerformance(metric: string, value: number, context?: LogContext): void {
  logger.performance(metric, value, context);
}

// User interaction logging
export function logUserInteraction(action: string, element: string, context?: LogContext): void {
  logger.userAction(`User interacted with ${element}: ${action}`, {
    ...context,
    action,
    element,
    component: "user-interaction",
  });
}

// API call logging
export function logApiCall(
  method: string,
  url: string,
  statusCode: number,
  duration: number,
  context?: LogContext,
): void {
  logger.apiCall(method, url, statusCode, duration, context);
}

// Security event logging
export function logSecurityEvent(event: string, context?: LogContext): void {
  logger.security(event, context);
}

// Business event logging
export function logBusinessEvent(event: string, context?: LogContext): void {
  logger.business(event, context);
}
