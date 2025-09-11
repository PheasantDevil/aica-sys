'use client';

import { AccessibleButton } from '@/components/ui/accessible-button';
import {
  Notification,
  NotificationManager,
  useNotifications,
} from '@/lib/notifications';
import { cn } from '@/lib/utils';
import { useTranslations } from 'next-intl';
import React, { useEffect, useRef, useState } from 'react';

interface NotificationCenterProps {
  className?: string;
  maxHeight?: string;
  showPreferences?: boolean;
}

export function NotificationCenter({
  className,
  maxHeight = '400px',
  showPreferences = true,
}: NotificationCenterProps) {
  const t = useTranslations('common');
  const { notifications, unreadCount, markAsRead, markAllAsRead, clearAll } =
    useNotifications();
  const [isOpen, setIsOpen] = useState(false);
  const [filter, setFilter] = useState<'all' | 'unread' | Notification['type']>(
    'all'
  );
  const [showPreferencesPanel, setShowPreferencesPanel] = useState(false);

  const buttonRef = useRef<HTMLButtonElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);

  // Close panel when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        panelRef.current &&
        !panelRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Filter notifications
  const filteredNotifications = React.useMemo(() => {
    switch (filter) {
      case 'unread':
        return notifications.filter(n => !n.read);
      case 'all':
        return notifications;
      default:
        return notifications.filter(n => n.type === filter);
    }
  }, [notifications, filter]);

  // Handle notification click
  const handleNotificationClick = (notification: Notification) => {
    if (!notification.read) {
      markAsRead(notification.id);
    }
  };

  // Handle notification action
  const handleNotificationAction = (
    notification: Notification,
    actionId: string
  ) => {
    const action = notification.actions?.find(a => a.id === actionId);
    if (action) {
      action.action();
      if (!notification.persistent) {
        // Remove notification after action
        setTimeout(() => {
          // This would be handled by the parent component
        }, 1000);
      }
    }
  };

  return (
    <div className={cn('relative', className)}>
      {/* Notification Button */}
      <button
        ref={buttonRef}
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'relative p-2 rounded-md hover:bg-accent transition-colors',
          'focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2'
        )}
        aria-expanded={isOpen}
        aria-label={`${t('notifications')} ${
          unreadCount > 0 ? `(${unreadCount} unread)` : ''
        }`}
      >
        <svg
          className='w-6 h-6'
          fill='none'
          stroke='currentColor'
          viewBox='0 0 24 24'
        >
          <path
            strokeLinecap='round'
            strokeLinejoin='round'
            strokeWidth={2}
            d='M15 17h5l-5 5v-5zM4.5 19.5a2.5 2.5 0 01-2.5-2.5V7a2.5 2.5 0 012.5-2.5h15a2.5 2.5 0 012.5 2.5v10a2.5 2.5 0 01-2.5 2.5h-15z'
          />
        </svg>

        {unreadCount > 0 && (
          <span className='absolute -top-1 -right-1 w-5 h-5 bg-destructive text-destructive-foreground text-xs rounded-full flex items-center justify-center'>
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {/* Notification Panel */}
      {isOpen && (
        <div
          ref={panelRef}
          className='absolute right-0 top-full mt-2 w-96 bg-popover border border-border rounded-lg shadow-lg z-50'
          style={{ maxHeight }}
        >
          {/* Header */}
          <div className='p-4 border-b border-border'>
            <div className='flex items-center justify-between'>
              <h3 className='text-lg font-semibold'>{t('notifications')}</h3>
              <div className='flex items-center gap-2'>
                {showPreferences && (
                  <button
                    onClick={() =>
                      setShowPreferencesPanel(!showPreferencesPanel)
                    }
                    className='p-1 hover:bg-accent rounded-md transition-colors'
                    aria-label={t('preferences')}
                  >
                    <svg
                      className='w-4 h-4'
                      fill='none'
                      stroke='currentColor'
                      viewBox='0 0 24 24'
                    >
                      <path
                        strokeLinecap='round'
                        strokeLinejoin='round'
                        strokeWidth={2}
                        d='M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z'
                      />
                      <path
                        strokeLinecap='round'
                        strokeLinejoin='round'
                        strokeWidth={2}
                        d='M15 12a3 3 0 11-6 0 3 3 0 016 0z'
                      />
                    </svg>
                  </button>
                )}
                <button
                  onClick={markAllAsRead}
                  className='text-sm text-muted-foreground hover:text-foreground transition-colors'
                  disabled={unreadCount === 0}
                >
                  {t('markAllRead')}
                </button>
                <button
                  onClick={clearAll}
                  className='text-sm text-muted-foreground hover:text-destructive transition-colors'
                  disabled={notifications.length === 0}
                >
                  {t('clearAll')}
                </button>
              </div>
            </div>

            {/* Filters */}
            <div className='mt-3 flex gap-2'>
              <button
                onClick={() => setFilter('all')}
                className={cn(
                  'px-3 py-1 text-xs rounded-full transition-colors',
                  filter === 'all'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-muted-foreground hover:bg-accent'
                )}
              >
                {t('all')} ({notifications.length})
              </button>
              <button
                onClick={() => setFilter('unread')}
                className={cn(
                  'px-3 py-1 text-xs rounded-full transition-colors',
                  filter === 'unread'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-muted-foreground hover:bg-accent'
                )}
              >
                {t('unread')} ({unreadCount})
              </button>
            </div>
          </div>

          {/* Notifications List */}
          <div className='max-h-80 overflow-y-auto'>
            {filteredNotifications.length === 0 ? (
              <div className='p-8 text-center text-muted-foreground'>
                <svg
                  className='w-12 h-12 mx-auto mb-4 opacity-50'
                  fill='none'
                  stroke='currentColor'
                  viewBox='0 0 24 24'
                >
                  <path
                    strokeLinecap='round'
                    strokeLinejoin='round'
                    strokeWidth={2}
                    d='M15 17h5l-5 5v-5zM4.5 19.5a2.5 2.5 0 01-2.5-2.5V7a2.5 2.5 0 012.5-2.5h15a2.5 2.5 0 012.5 2.5v10a2.5 2.5 0 01-2.5 2.5h-15z'
                  />
                </svg>
                <p>{t('noNotifications')}</p>
              </div>
            ) : (
              <div className='divide-y divide-border'>
                {filteredNotifications.map(notification => (
                  <NotificationItem
                    key={notification.id}
                    notification={notification}
                    onClick={() => handleNotificationClick(notification)}
                    onAction={actionId =>
                      handleNotificationAction(notification, actionId)
                    }
                  />
                ))}
              </div>
            )}
          </div>

          {/* Preferences Panel */}
          {showPreferencesPanel && (
            <NotificationPreferences
              onClose={() => setShowPreferencesPanel(false)}
            />
          )}
        </div>
      )}
    </div>
  );
}

// Individual Notification Item
interface NotificationItemProps {
  notification: Notification;
  onClick: () => void;
  onAction: (actionId: string) => void;
}

function NotificationItem({
  notification,
  onClick,
  onAction,
}: NotificationItemProps) {
  const t = useTranslations('common');

  const getTypeIcon = (type: Notification['type']) => {
    switch (type) {
      case 'success':
        return (
          <svg
            className='w-5 h-5 text-green-500'
            fill='currentColor'
            viewBox='0 0 20 20'
          >
            <path
              fillRule='evenodd'
              d='M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z'
              clipRule='evenodd'
            />
          </svg>
        );
      case 'error':
        return (
          <svg
            className='w-5 h-5 text-red-500'
            fill='currentColor'
            viewBox='0 0 20 20'
          >
            <path
              fillRule='evenodd'
              d='M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z'
              clipRule='evenodd'
            />
          </svg>
        );
      case 'warning':
        return (
          <svg
            className='w-5 h-5 text-yellow-500'
            fill='currentColor'
            viewBox='0 0 20 20'
          >
            <path
              fillRule='evenodd'
              d='M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z'
              clipRule='evenodd'
            />
          </svg>
        );
      default:
        return (
          <svg
            className='w-5 h-5 text-blue-500'
            fill='currentColor'
            viewBox='0 0 20 20'
          >
            <path
              fillRule='evenodd'
              d='M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z'
              clipRule='evenodd'
            />
          </svg>
        );
    }
  };

  const formatTimestamp = (timestamp: Date) => {
    const now = new Date();
    const diff = now.getTime() - timestamp.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return t('justNow');
    if (minutes < 60) return t('minutesAgo', { count: minutes });
    if (hours < 24) return t('hoursAgo', { count: hours });
    return t('daysAgo', { count: days });
  };

  return (
    <div
      className={cn(
        'p-4 hover:bg-accent transition-colors cursor-pointer',
        !notification.read && 'bg-accent/50'
      )}
      onClick={onClick}
    >
      <div className='flex items-start gap-3'>
        <div className='flex-shrink-0 mt-0.5'>
          {getTypeIcon(notification.type)}
        </div>

        <div className='flex-1 min-w-0'>
          <div className='flex items-start justify-between'>
            <h4
              className={cn(
                'text-sm font-medium',
                !notification.read && 'font-semibold'
              )}
            >
              {notification.title}
            </h4>
            <span className='text-xs text-muted-foreground ml-2'>
              {formatTimestamp(notification.timestamp)}
            </span>
          </div>

          <p className='text-sm text-muted-foreground mt-1'>
            {notification.message}
          </p>

          {/* Actions */}
          {notification.actions && notification.actions.length > 0 && (
            <div className='mt-3 flex gap-2'>
              {notification.actions.map(action => (
                <AccessibleButton
                  key={action.id}
                  size='sm'
                  variant={action.variant || 'secondary'}
                  onClick={e => {
                    e.stopPropagation();
                    onAction(action.id);
                  }}
                >
                  {action.label}
                </AccessibleButton>
              ))}
            </div>
          )}
        </div>

        {!notification.read && (
          <div className='w-2 h-2 bg-primary rounded-full flex-shrink-0 mt-2' />
        )}
      </div>
    </div>
  );
}

// Notification Preferences Component
interface NotificationPreferencesProps {
  onClose: () => void;
}

function NotificationPreferences({ onClose }: NotificationPreferencesProps) {
  const t = useTranslations('common');
  const [preferences, setPreferences] = React.useState(
    NotificationManager.prototype.getPreferences()
  );

  const handlePreferenceChange = (key: string, value: any) => {
    const newPreferences = { ...preferences };

    if (key.includes('.')) {
      const [parent, child] = key.split('.');
      (newPreferences as any)[parent][child] = value;
    } else {
      (newPreferences as any)[key] = value;
    }

    setPreferences(newPreferences);
    notificationManager.updatePreferences(newPreferences);
  };

  return (
    <div className='p-4 border-t border-border bg-muted/50'>
      <div className='flex items-center justify-between mb-4'>
        <h4 className='font-medium'>{t('notificationPreferences')}</h4>
        <button
          onClick={onClose}
          className='p-1 hover:bg-accent rounded-md transition-colors'
        >
          <svg
            className='w-4 h-4'
            fill='none'
            stroke='currentColor'
            viewBox='0 0 24 24'
          >
            <path
              strokeLinecap='round'
              strokeLinejoin='round'
              strokeWidth={2}
              d='M6 18L18 6M6 6l12 12'
            />
          </svg>
        </button>
      </div>

      <div className='space-y-4'>
        {/* General Settings */}
        <div className='space-y-3'>
          <h5 className='text-sm font-medium'>{t('generalSettings')}</h5>

          <label className='flex items-center gap-3'>
            <input
              type='checkbox'
              checked={preferences.inApp}
              onChange={e => handlePreferenceChange('inApp', e.target.checked)}
              className='rounded border-input'
            />
            <span className='text-sm'>{t('inAppNotifications')}</span>
          </label>

          <label className='flex items-center gap-3'>
            <input
              type='checkbox'
              checked={preferences.email}
              onChange={e => handlePreferenceChange('email', e.target.checked)}
              className='rounded border-input'
            />
            <span className='text-sm'>{t('emailNotifications')}</span>
          </label>

          <label className='flex items-center gap-3'>
            <input
              type='checkbox'
              checked={preferences.push}
              onChange={e => handlePreferenceChange('push', e.target.checked)}
              className='rounded border-input'
            />
            <span className='text-sm'>{t('pushNotifications')}</span>
          </label>
        </div>

        {/* Category Settings */}
        <div className='space-y-3'>
          <h5 className='text-sm font-medium'>{t('categories')}</h5>

          {Object.entries(preferences.categories).map(([category, enabled]) => (
            <label key={category} className='flex items-center gap-3'>
              <input
                type='checkbox'
                checked={enabled}
                onChange={e =>
                  handlePreferenceChange(
                    `categories.${category}`,
                    e.target.checked
                  )
                }
                className='rounded border-input'
              />
              <span className='text-sm capitalize'>{t(category)}</span>
            </label>
          ))}
        </div>

        {/* Frequency */}
        <div className='space-y-3'>
          <h5 className='text-sm font-medium'>{t('frequency')}</h5>

          <select
            value={preferences.frequency}
            onChange={e => handlePreferenceChange('frequency', e.target.value)}
            className='w-full px-3 py-2 text-sm border border-input rounded-md bg-background'
          >
            <option value='immediate'>{t('immediate')}</option>
            <option value='daily'>{t('daily')}</option>
            <option value='weekly'>{t('weekly')}</option>
            <option value='never'>{t('never')}</option>
          </select>
        </div>
      </div>
    </div>
  );
}
