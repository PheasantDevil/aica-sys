interface SecurityEvent {
  id: string;
  timestamp: Date;
  type: SecurityEventType;
  severity: SecuritySeverity;
  userId?: string;
  ipAddress: string;
  userAgent: string;
  details: Record<string, any>;
  resolved: boolean;
}

enum SecurityEventType {
  LOGIN_SUCCESS = 'LOGIN_SUCCESS',
  LOGIN_FAILURE = 'LOGIN_FAILURE',
  LOGOUT = 'LOGOUT',
  PASSWORD_CHANGE = 'PASSWORD_CHANGE',
  RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED',
  CSRF_VIOLATION = 'CSRF_VIOLATION',
  SUSPICIOUS_ACTIVITY = 'SUSPICIOUS_ACTIVITY',
  UNAUTHORIZED_ACCESS = 'UNAUTHORIZED_ACCESS',
  DATA_BREACH_ATTEMPT = 'DATA_BREACH_ATTEMPT',
  MALICIOUS_INPUT = 'MALICIOUS_INPUT',
}

enum SecuritySeverity {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL',
}

class SecurityAuditLogger {
  private events: SecurityEvent[] = [];
  private maxEvents = 10000; // 最大イベント数

  private generateId(): string {
    return `sec_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private cleanup(): void {
    if (this.events.length > this.maxEvents) {
      // 古いイベントを削除（最新のイベントを保持）
      this.events = this.events
        .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
        .slice(0, this.maxEvents);
    }
  }

  logEvent(
    type: SecurityEventType,
    severity: SecuritySeverity,
    details: Record<string, any>,
    userId?: string,
    ipAddress?: string,
    userAgent?: string
  ): string {
    const event: SecurityEvent = {
      id: this.generateId(),
      timestamp: new Date(),
      type,
      severity,
      userId,
      ipAddress: ipAddress || 'unknown',
      userAgent: userAgent || 'unknown',
      details,
      resolved: false,
    };

    this.events.push(event);
    this.cleanup();

    // 本番環境では外部ログサービスに送信
    if (process.env.NODE_ENV === 'production') {
      this.sendToExternalService(event);
    } else {
      console.warn('Security Event:', event);
    }

    return event.id;
  }

  private async sendToExternalService(event: SecurityEvent): Promise<void> {
    try {
      // 実際の実装では、Sentry、DataDog、CloudWatch等に送信
      console.log('Sending security event to external service:', event);
    } catch (error) {
      console.error('Failed to send security event:', error);
    }
  }

  getEvents(filters?: {
    type?: SecurityEventType;
    severity?: SecuritySeverity;
    userId?: string;
    resolved?: boolean;
    startDate?: Date;
    endDate?: Date;
  }): SecurityEvent[] {
    let filteredEvents = [...this.events];

    if (filters) {
      if (filters.type) {
        filteredEvents = filteredEvents.filter(event => event.type === filters.type);
      }
      if (filters.severity) {
        filteredEvents = filteredEvents.filter(event => event.severity === filters.severity);
      }
      if (filters.userId) {
        filteredEvents = filteredEvents.filter(event => event.userId === filters.userId);
      }
      if (filters.resolved !== undefined) {
        filteredEvents = filteredEvents.filter(event => event.resolved === filters.resolved);
      }
      if (filters.startDate) {
        filteredEvents = filteredEvents.filter(event => event.timestamp >= filters.startDate!);
      }
      if (filters.endDate) {
        filteredEvents = filteredEvents.filter(event => event.timestamp <= filters.endDate!);
      }
    }

    return filteredEvents.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
  }

  markAsResolved(eventId: string): boolean {
    const event = this.events.find(e => e.id === eventId);
    if (event) {
      event.resolved = true;
      return true;
    }
    return false;
  }

  getStats(): {
    totalEvents: number;
    eventsByType: Record<SecurityEventType, number>;
    eventsBySeverity: Record<SecuritySeverity, number>;
    unresolvedEvents: number;
  } {
    const stats = {
      totalEvents: this.events.length,
      eventsByType: {} as Record<SecurityEventType, number>,
      eventsBySeverity: {} as Record<SecuritySeverity, number>,
      unresolvedEvents: 0,
    };

    // 初期化
    Object.values(SecurityEventType).forEach(type => {
      stats.eventsByType[type] = 0;
    });
    Object.values(SecuritySeverity).forEach(severity => {
      stats.eventsBySeverity[severity] = 0;
    });

    // 集計
    this.events.forEach(event => {
      stats.eventsByType[event.type]++;
      stats.eventsBySeverity[event.severity]++;
      if (!event.resolved) {
        stats.unresolvedEvents++;
      }
    });

    return stats;
  }
}

export const securityAuditLogger = new SecurityAuditLogger();

// セキュリティイベントのヘルパー関数
export const securityEvents = {
  logLoginSuccess: (userId: string, ipAddress: string, userAgent: string) => {
    return securityAuditLogger.logEvent(
      SecurityEventType.LOGIN_SUCCESS,
      SecuritySeverity.LOW,
      { userId },
      userId,
      ipAddress,
      userAgent
    );
  },

  logLoginFailure: (email: string, ipAddress: string, userAgent: string, reason: string) => {
    return securityAuditLogger.logEvent(
      SecurityEventType.LOGIN_FAILURE,
      SecuritySeverity.MEDIUM,
      { email, reason },
      undefined,
      ipAddress,
      userAgent
    );
  },

  logRateLimitExceeded: (ipAddress: string, userAgent: string, endpoint: string) => {
    return securityAuditLogger.logEvent(
      SecurityEventType.RATE_LIMIT_EXCEEDED,
      SecuritySeverity.MEDIUM,
      { endpoint },
      undefined,
      ipAddress,
      userAgent
    );
  },

  logCSRFViolation: (userId: string, ipAddress: string, userAgent: string) => {
    return securityAuditLogger.logEvent(
      SecurityEventType.CSRF_VIOLATION,
      SecuritySeverity.HIGH,
      { userId },
      userId,
      ipAddress,
      userAgent
    );
  },

  logSuspiciousActivity: (details: Record<string, any>, ipAddress: string, userAgent: string) => {
    return securityAuditLogger.logEvent(
      SecurityEventType.SUSPICIOUS_ACTIVITY,
      SecuritySeverity.HIGH,
      details,
      undefined,
      ipAddress,
      userAgent
    );
  },

  logMaliciousInput: (input: string, ipAddress: string, userAgent: string) => {
    return securityAuditLogger.logEvent(
      SecurityEventType.MALICIOUS_INPUT,
      SecuritySeverity.HIGH,
      { input: input.substring(0, 100) }, // 入力の最初の100文字のみ記録
      undefined,
      ipAddress,
      userAgent
    );
  },
};

export { SecurityEventType, SecuritySeverity };
