'use client';

import { AccessibleButton } from '@/components/ui/accessible-button';
import { cn } from '@/lib/utils';
import { useTranslations } from 'next-intl';
import { useEffect, useState } from 'react';

interface AdminDashboardProps {
  className?: string;
}

interface SystemStats {
  users: {
    total: number;
    active: number;
    new: number;
  };
  content: {
    articles: number;
    newsletters: number;
    comments: number;
  };
  performance: {
    avgResponseTime: number;
    uptime: number;
    errorRate: number;
  };
  revenue: {
    monthly: number;
    yearly: number;
    growth: number;
  };
}

interface LogEntry {
  id: string;
  timestamp: Date;
  level: 'error' | 'warning' | 'info' | 'debug';
  message: string;
  component: string;
  context?: Record<string, any>;
}

export function AdminDashboard({ className }: AdminDashboardProps) {
  const t = useTranslations('common');
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState<
    'overview' | 'logs' | 'users' | 'content' | 'settings'
  >('overview');
  const [logFilter, setLogFilter] = useState<
    'all' | 'error' | 'warning' | 'info'
  >('all');

  // Load dashboard data
  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      // Simulate API calls
      const [statsData, logsData] = await Promise.all([
        fetchSystemStats(),
        fetchLogs(),
      ]);

      setStats(statsData);
      setLogs(logsData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchSystemStats = async (): Promise<SystemStats> => {
    // Simulate API call
    return {
      users: {
        total: 1250,
        active: 890,
        new: 45,
      },
      content: {
        articles: 156,
        newsletters: 23,
        comments: 2340,
      },
      performance: {
        avgResponseTime: 245,
        uptime: 99.9,
        errorRate: 0.1,
      },
      revenue: {
        monthly: 12500,
        yearly: 150000,
        growth: 12.5,
      },
    };
  };

  const fetchLogs = async (): Promise<LogEntry[]> => {
    // Simulate API call
    return [
      {
        id: '1',
        timestamp: new Date(),
        level: 'error',
        message: 'Database connection failed',
        component: 'database',
        context: { error: 'Connection timeout' },
      },
      {
        id: '2',
        timestamp: new Date(Date.now() - 300000),
        level: 'warning',
        message: 'High memory usage detected',
        component: 'system',
        context: { usage: '85%' },
      },
      {
        id: '3',
        timestamp: new Date(Date.now() - 600000),
        level: 'info',
        message: 'User login successful',
        component: 'auth',
        context: { userId: 'user123' },
      },
    ];
  };

  const filteredLogs = logs.filter(
    log => logFilter === 'all' || log.level === logFilter
  );

  if (isLoading) {
    return (
      <div className={cn('p-6', className)}>
        <div className='animate-pulse space-y-4'>
          <div className='h-8 bg-muted rounded w-1/4'></div>
          <div className='grid grid-cols-1 md:grid-cols-4 gap-4'>
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className='h-24 bg-muted rounded'></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      <div className='flex items-center justify-between'>
        <h1 className='text-3xl font-bold'>Admin Dashboard</h1>
        <div className='flex items-center gap-4'>
          <AccessibleButton onClick={loadDashboardData} loading={isLoading}>
            Refresh
          </AccessibleButton>
          <div className='text-sm text-muted-foreground'>
            Last updated: {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className='border-b border-border'>
        <nav className='flex space-x-8'>
          {[
            { id: 'overview', label: 'Overview' },
            { id: 'logs', label: 'Logs' },
            { id: 'users', label: 'Users' },
            { id: 'content', label: 'Content' },
            { id: 'settings', label: 'Settings' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setSelectedTab(tab.id as any)}
              className={cn(
                'py-2 px-1 border-b-2 font-medium text-sm transition-colors',
                selectedTab === tab.id
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'
              )}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className='space-y-6'>
        {selectedTab === 'overview' && stats && <OverviewTab stats={stats} />}

        {selectedTab === 'logs' && (
          <LogsTab
            logs={filteredLogs}
            filter={logFilter}
            onFilterChange={setLogFilter}
          />
        )}

        {selectedTab === 'users' && <UsersTab />}

        {selectedTab === 'content' && <ContentTab />}

        {selectedTab === 'settings' && <SettingsTab />}
      </div>
    </div>
  );
}

// Overview Tab Component
interface OverviewTabProps {
  stats: SystemStats;
}

function OverviewTab({ stats }: OverviewTabProps) {
  return (
    <div className='space-y-6'>
      {/* Stats Cards */}
      <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6'>
        <StatCard
          title='Total Users'
          value={stats.users.total.toLocaleString()}
          change={`+${stats.users.new} this week`}
          trend='up'
        />
        <StatCard
          title='Active Users'
          value={stats.users.active.toLocaleString()}
          change={`${Math.round(
            (stats.users.active / stats.users.total) * 100
          )}% of total`}
          trend='up'
        />
        <StatCard
          title='Articles'
          value={stats.content.articles.toLocaleString()}
          change='12 published this week'
          trend='up'
        />
        <StatCard
          title='Monthly Revenue'
          value={`$${stats.revenue.monthly.toLocaleString()}`}
          change={`${stats.revenue.growth}% growth`}
          trend='up'
        />
      </div>

      {/* Performance Metrics */}
      <div className='grid grid-cols-1 lg:grid-cols-3 gap-6'>
        <div className='bg-card p-6 rounded-lg border'>
          <h3 className='text-lg font-semibold mb-4'>Performance</h3>
          <div className='space-y-4'>
            <div className='flex justify-between'>
              <span className='text-muted-foreground'>Avg Response Time</span>
              <span className='font-medium'>
                {stats.performance.avgResponseTime}ms
              </span>
            </div>
            <div className='flex justify-between'>
              <span className='text-muted-foreground'>Uptime</span>
              <span className='font-medium text-green-600'>
                {stats.performance.uptime}%
              </span>
            </div>
            <div className='flex justify-between'>
              <span className='text-muted-foreground'>Error Rate</span>
              <span className='font-medium text-red-600'>
                {stats.performance.errorRate}%
              </span>
            </div>
          </div>
        </div>

        <div className='bg-card p-6 rounded-lg border'>
          <h3 className='text-lg font-semibold mb-4'>Content</h3>
          <div className='space-y-4'>
            <div className='flex justify-between'>
              <span className='text-muted-foreground'>Articles</span>
              <span className='font-medium'>{stats.content.articles}</span>
            </div>
            <div className='flex justify-between'>
              <span className='text-muted-foreground'>Newsletters</span>
              <span className='font-medium'>{stats.content.newsletters}</span>
            </div>
            <div className='flex justify-between'>
              <span className='text-muted-foreground'>Comments</span>
              <span className='font-medium'>{stats.content.comments}</span>
            </div>
          </div>
        </div>

        <div className='bg-card p-6 rounded-lg border'>
          <h3 className='text-lg font-semibold mb-4'>Revenue</h3>
          <div className='space-y-4'>
            <div className='flex justify-between'>
              <span className='text-muted-foreground'>Monthly</span>
              <span className='font-medium'>
                ${stats.revenue.monthly.toLocaleString()}
              </span>
            </div>
            <div className='flex justify-between'>
              <span className='text-muted-foreground'>Yearly</span>
              <span className='font-medium'>
                ${stats.revenue.yearly.toLocaleString()}
              </span>
            </div>
            <div className='flex justify-between'>
              <span className='text-muted-foreground'>Growth</span>
              <span className='font-medium text-green-600'>
                +{stats.revenue.growth}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Stat Card Component
interface StatCardProps {
  title: string;
  value: string;
  change: string;
  trend: 'up' | 'down' | 'neutral';
}

function StatCard({ title, value, change, trend }: StatCardProps) {
  const trendColor = {
    up: 'text-green-600',
    down: 'text-red-600',
    neutral: 'text-muted-foreground',
  }[trend];

  return (
    <div className='bg-card p-6 rounded-lg border'>
      <h3 className='text-sm font-medium text-muted-foreground mb-2'>
        {title}
      </h3>
      <div className='text-2xl font-bold mb-1'>{value}</div>
      <div className={`text-sm ${trendColor}`}>{change}</div>
    </div>
  );
}

// Logs Tab Component
interface LogsTabProps {
  logs: LogEntry[];
  filter: 'all' | 'error' | 'warning' | 'info';
  onFilterChange: (filter: 'all' | 'error' | 'warning' | 'info') => void;
}

function LogsTab({ logs, filter, onFilterChange }: LogsTabProps) {
  const getLevelColor = (level: string) => {
    switch (level) {
      case 'error':
        return 'text-red-600 bg-red-50';
      case 'warning':
        return 'text-yellow-600 bg-yellow-50';
      case 'info':
        return 'text-blue-600 bg-blue-50';
      case 'debug':
        return 'text-gray-600 bg-gray-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className='space-y-4'>
      {/* Filters */}
      <div className='flex items-center gap-4'>
        <select
          value={filter}
          onChange={e =>
            onFilterChange(
              e.target.value as 'all' | 'error' | 'warning' | 'info'
            )
          }
          className='px-3 py-2 border border-input rounded-md bg-background'
        >
          <option value='all'>All Levels</option>
          <option value='error'>Errors</option>
          <option value='warning'>Warnings</option>
          <option value='info'>Info</option>
        </select>
        <div className='text-sm text-muted-foreground'>
          {logs.length} log entries
        </div>
      </div>

      {/* Logs List */}
      <div className='bg-card border rounded-lg'>
        <div className='max-h-96 overflow-y-auto'>
          {logs.length === 0 ? (
            <div className='p-8 text-center text-muted-foreground'>
              No logs found
            </div>
          ) : (
            <div className='divide-y divide-border'>
              {logs.map(log => (
                <div key={log.id} className='p-4 hover:bg-muted/50'>
                  <div className='flex items-start gap-4'>
                    <div
                      className={`px-2 py-1 rounded text-xs font-medium ${getLevelColor(
                        log.level
                      )}`}
                    >
                      {log.level.toUpperCase()}
                    </div>
                    <div className='flex-1 min-w-0'>
                      <div className='flex items-center gap-2 mb-1'>
                        <span className='text-sm font-medium'>
                          {log.component}
                        </span>
                        <span className='text-xs text-muted-foreground'>
                          {log.timestamp.toLocaleString()}
                        </span>
                      </div>
                      <p className='text-sm text-foreground'>{log.message}</p>
                      {log.context && (
                        <details className='mt-2'>
                          <summary className='text-xs text-muted-foreground cursor-pointer'>
                            Context
                          </summary>
                          <pre className='mt-2 text-xs bg-muted p-2 rounded overflow-x-auto'>
                            {JSON.stringify(log.context, null, 2)}
                          </pre>
                        </details>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Placeholder components for other tabs
function UsersTab() {
  return (
    <div className='p-8 text-center text-muted-foreground'>
      <h3 className='text-lg font-semibold mb-2'>User Management</h3>
      <p>User management features will be implemented here.</p>
    </div>
  );
}

function ContentTab() {
  return (
    <div className='p-8 text-center text-muted-foreground'>
      <h3 className='text-lg font-semibold mb-2'>Content Management</h3>
      <p>Content management features will be implemented here.</p>
    </div>
  );
}

function SettingsTab() {
  return (
    <div className='p-8 text-center text-muted-foreground'>
      <h3 className='text-lg font-semibold mb-2'>System Settings</h3>
      <p>System settings will be implemented here.</p>
    </div>
  );
}
