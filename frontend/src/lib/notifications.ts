export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  persistent: boolean;
  actions?: NotificationAction[];
  metadata?: Record<string, any>;
}

export interface NotificationAction {
  id: string;
  label: string;
  action: () => void;
  variant?: 'primary' | 'secondary' | 'destructive';
}

export interface NotificationPreferences {
  email: boolean;
  push: boolean;
  inApp: boolean;
  categories: {
    articles: boolean;
    comments: boolean;
    likes: boolean;
    mentions: boolean;
    system: boolean;
    marketing: boolean;
  };
  frequency: 'immediate' | 'daily' | 'weekly' | 'never';
  quietHours: {
    enabled: boolean;
    start: string; // HH:MM format
    end: string; // HH:MM format
    timezone: string;
  };
}

export class NotificationManager {
  private notifications: Notification[] = [];
  private listeners: Set<(notifications: Notification[]) => void> = new Set();
  private preferences: NotificationPreferences = this.getDefaultPreferences();

  constructor() {
    this.loadNotifications();
    this.loadPreferences();
  }

  // Subscribe to notification changes
  subscribe(listener: (notifications: Notification[]) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  // Notify listeners
  private notify(): void {
    this.listeners.forEach(listener => listener([...this.notifications]));
  }

  // Add a new notification
  add(notification: Omit<Notification, 'id' | 'timestamp' | 'read'>): string {
    const id = this.generateId();
    const newNotification: Notification = {
      ...notification,
      id,
      timestamp: new Date(),
      read: false,
    };

    this.notifications.unshift(newNotification);
    this.saveNotifications();
    this.notify();

    // Auto-remove non-persistent notifications after 5 seconds
    if (!newNotification.persistent) {
      setTimeout(() => {
        this.remove(id);
      }, 5000);
    }

    return id;
  }

  // Remove a notification
  remove(id: string): void {
    this.notifications = this.notifications.filter(n => n.id !== id);
    this.saveNotifications();
    this.notify();
  }

  // Mark notification as read
  markAsRead(id: string): void {
    const notification = this.notifications.find(n => n.id === id);
    if (notification) {
      notification.read = true;
      this.saveNotifications();
      this.notify();
    }
  }

  // Mark all notifications as read
  markAllAsRead(): void {
    this.notifications.forEach(n => n.read = true);
    this.saveNotifications();
    this.notify();
  }

  // Clear all notifications
  clearAll(): void {
    this.notifications = [];
    this.saveNotifications();
    this.notify();
  }

  // Get unread count
  getUnreadCount(): number {
    return this.notifications.filter(n => !n.read).length;
  }

  // Get notifications by type
  getByType(type: Notification['type']): Notification[] {
    return this.notifications.filter(n => n.type === type);
  }

  // Get unread notifications
  getUnread(): Notification[] {
    return this.notifications.filter(n => !n.read);
  }

  // Get all notifications
  getAll(): Notification[] {
    return [...this.notifications];
  }

  // Update preferences
  updatePreferences(preferences: Partial<NotificationPreferences>): void {
    this.preferences = { ...this.preferences, ...preferences };
    this.savePreferences();
  }

  // Get preferences
  getPreferences(): NotificationPreferences {
    return { ...this.preferences };
  }

  // Check if notifications should be sent based on preferences
  shouldSendNotification(category: keyof NotificationPreferences['categories']): boolean {
    if (!this.preferences.inApp) return false;
    if (!this.preferences.categories[category]) return false;
    
    // Check quiet hours
    if (this.preferences.quietHours.enabled) {
      const now = new Date();
      const currentTime = now.toLocaleTimeString('en-US', { 
        hour12: false, 
        timeZone: this.preferences.quietHours.timezone 
      });
      
      const start = this.preferences.quietHours.start;
      const end = this.preferences.quietHours.end;
      
      if (this.isTimeInRange(currentTime, start, end)) {
        return false;
      }
    }

    return true;
  }

  // Helper method to check if current time is in quiet hours range
  private isTimeInRange(current: string, start: string, end: string): boolean {
    const currentMinutes = this.timeToMinutes(current);
    const startMinutes = this.timeToMinutes(start);
    const endMinutes = this.timeToMinutes(end);

    if (startMinutes <= endMinutes) {
      return currentMinutes >= startMinutes && currentMinutes <= endMinutes;
    } else {
      // Handle overnight range (e.g., 22:00 to 06:00)
      return currentMinutes >= startMinutes || currentMinutes <= endMinutes;
    }
  }

  private timeToMinutes(time: string): number {
    const [hours, minutes] = time.split(':').map(Number);
    return hours * 60 + minutes;
  }

  // Generate unique ID
  private generateId(): string {
    return `notification_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // Default preferences
  private getDefaultPreferences(): NotificationPreferences {
    return {
      email: true,
      push: true,
      inApp: true,
      categories: {
        articles: true,
        comments: true,
        likes: true,
        mentions: true,
        system: true,
        marketing: false,
      },
      frequency: 'immediate',
      quietHours: {
        enabled: false,
        start: '22:00',
        end: '08:00',
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      },
    };
  }

  // Load notifications from localStorage
  private loadNotifications(): void {
    try {
      const stored = localStorage.getItem('notifications');
      if (stored) {
        const parsed = JSON.parse(stored);
        this.notifications = parsed.map((n: any) => ({
          ...n,
          timestamp: new Date(n.timestamp),
        }));
      }
    } catch (error) {
      console.error('Failed to load notifications:', error);
    }
  }

  // Save notifications to localStorage
  private saveNotifications(): void {
    try {
      localStorage.setItem('notifications', JSON.stringify(this.notifications));
    } catch (error) {
      console.error('Failed to save notifications:', error);
    }
  }

  // Load preferences from localStorage
  private loadPreferences(): void {
    try {
      const stored = localStorage.getItem('notification_preferences');
      if (stored) {
        this.preferences = { ...this.preferences, ...JSON.parse(stored) };
      }
    } catch (error) {
      console.error('Failed to load notification preferences:', error);
    }
  }

  // Save preferences to localStorage
  private savePreferences(): void {
    try {
      localStorage.setItem('notification_preferences', JSON.stringify(this.preferences));
    } catch (error) {
      console.error('Failed to save notification preferences:', error);
    }
  }
}

// Global notification manager instance
export const notificationManager = new NotificationManager();

// Notification types for common use cases
export const NotificationTypes = {
  // Article notifications
  ARTICLE_PUBLISHED: (title: string) => ({
    type: 'info' as const,
    title: 'New Article Published',
    message: `"${title}" has been published`,
    persistent: false,
    metadata: { category: 'articles' },
  }),

  ARTICLE_LIKED: (title: string, author: string) => ({
    type: 'success' as const,
    title: 'Article Liked',
    message: `${author} liked your article "${title}"`,
    persistent: false,
    metadata: { category: 'likes' },
  }),

  // Comment notifications
  COMMENT_ADDED: (articleTitle: string, author: string) => ({
    type: 'info' as const,
    title: 'New Comment',
    message: `${author} commented on "${articleTitle}"`,
    persistent: true,
    metadata: { category: 'comments' },
  }),

  COMMENT_LIKED: (author: string) => ({
    type: 'success' as const,
    title: 'Comment Liked',
    message: `${author} liked your comment`,
    persistent: false,
    metadata: { category: 'likes' },
  }),

  // System notifications
  SYSTEM_UPDATE: (message: string) => ({
    type: 'info' as const,
    title: 'System Update',
    message,
    persistent: true,
    metadata: { category: 'system' },
  }),

  SYSTEM_ERROR: (message: string) => ({
    type: 'error' as const,
    title: 'System Error',
    message,
    persistent: true,
    metadata: { category: 'system' },
  }),

  // Marketing notifications
  NEWSLETTER_SENT: (title: string) => ({
    type: 'info' as const,
    title: 'Newsletter Sent',
    message: `"${title}" has been sent to subscribers`,
    persistent: false,
    metadata: { category: 'marketing' },
  }),

  // Subscription notifications
  SUBSCRIPTION_EXPIRING: (daysLeft: number) => ({
    type: 'warning' as const,
    title: 'Subscription Expiring',
    message: `Your subscription expires in ${daysLeft} days`,
    persistent: true,
    metadata: { category: 'system' },
  }),

  SUBSCRIPTION_RENEWED: () => ({
    type: 'success' as const,
    title: 'Subscription Renewed',
    message: 'Your subscription has been successfully renewed',
    persistent: false,
    metadata: { category: 'system' },
  }),
};

// React hook for notifications
export function useNotifications() {
  const [notifications, setNotifications] = React.useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = React.useState(0);

  React.useEffect(() => {
    const unsubscribe = notificationManager.subscribe((newNotifications) => {
      setNotifications(newNotifications);
      setUnreadCount(notificationManager.getUnreadCount());
    });

    // Initialize with current notifications
    setNotifications(notificationManager.getAll());
    setUnreadCount(notificationManager.getUnreadCount());

    return unsubscribe;
  }, []);

  return {
    notifications,
    unreadCount,
    add: notificationManager.add.bind(notificationManager),
    remove: notificationManager.remove.bind(notificationManager),
    markAsRead: notificationManager.markAsRead.bind(notificationManager),
    markAllAsRead: notificationManager.markAllAsRead.bind(notificationManager),
    clearAll: notificationManager.clearAll.bind(notificationManager),
  };
}

// Import React for the hook
import React from 'react';
