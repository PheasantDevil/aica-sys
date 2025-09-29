'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AlertTriangle, CheckCircle, Clock, Server, Users, Activity, AlertCircle } from 'lucide-react';

interface HealthCheck {
  status: string;
  response_time: number;
  message: string;
  timestamp: string;
  details?: Record<string, any>;
}

interface Metric {
  name: string;
  value: number | string;
  type: string;
  timestamp: string;
  tags?: Record<string, string>;
}

interface Alert {
  id: string;
  level: string;
  title: string;
  message: string;
  service: string;
  timestamp: string;
  resolved: boolean;
  resolved_at?: string;
}

interface DashboardData {
  health_status: {
    status: string;
    checks: Record<string, HealthCheck>;
  };
  metrics: {
    system: Metric[];
    application: Metric[];
    business: Metric[];
  };
  alerts: {
    active: Alert[];
    total_active: number;
  };
  timestamp: string;
}

export function MonitoringDashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/monitoring/dashboard', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setDashboardData(data);
      setLastUpdated(new Date());
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    
    // 30秒ごとにデータを更新
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-500';
      case 'warning':
        return 'bg-yellow-500';
      case 'critical':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case 'critical':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-500" />;
    }
  };

  const getAlertLevelColor = (level: string) => {
    switch (level) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'info':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const formatValue = (value: number | string, name: string) => {
    if (typeof value === 'number') {
      if (name.includes('percent') || name.includes('rate')) {
        return `${value.toFixed(1)}%`;
      }
      if (name.includes('time') || name.includes('duration')) {
        return `${value.toFixed(3)}s`;
      }
      if (name.includes('count') || name.includes('bytes')) {
        return value.toLocaleString();
      }
      return value.toFixed(2);
    }
    return value;
  };

  if (loading && !dashboardData) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Activity className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-500" />
          <p className="text-gray-600">Loading monitoring data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="h-8 w-8 mx-auto mb-4 text-red-500" />
          <p className="text-red-600 mb-4">Error loading monitoring data</p>
          <p className="text-sm text-gray-500 mb-4">{error}</p>
          <Button onClick={fetchDashboardData} variant="outline">
            Retry
          </Button>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-gray-600">No monitoring data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Monitoring Dashboard</h1>
          <p className="text-gray-600">
            System health and performance monitoring
          </p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-500">
            Last updated: {lastUpdated?.toLocaleString()}
          </p>
          <Button onClick={fetchDashboardData} variant="outline" size="sm">
            Refresh
          </Button>
        </div>
      </div>

      {/* Overall Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Server className="h-5 w-5" />
            System Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            {getStatusIcon(dashboardData.health_status.status)}
            <div>
              <h3 className="text-lg font-semibold capitalize">
                {dashboardData.health_status.status}
              </h3>
              <p className="text-sm text-gray-600">
                Overall system health status
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Health Checks */}
      <Card>
        <CardHeader>
          <CardTitle>Health Checks</CardTitle>
          <CardDescription>
            Status of individual system components
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(dashboardData.health_status.checks).map(([service, check]) => (
              <div key={service} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium capitalize">{service.replace('_', ' ')}</h4>
                  <Badge className={getStatusColor(check.status)}>
                    {check.status}
                  </Badge>
                </div>
                <p className="text-sm text-gray-600 mb-2">{check.message}</p>
                <div className="text-xs text-gray-500">
                  Response time: {check.response_time.toFixed(3)}s
                </div>
                {check.details && (
                  <div className="mt-2 text-xs">
                    {Object.entries(check.details).map(([key, value]) => (
                      <div key={key}>
                        {key}: {typeof value === 'number' ? value.toFixed(1) : value}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Metrics and Alerts */}
      <Tabs defaultValue="metrics" className="space-y-4">
        <TabsList>
          <TabsTrigger value="metrics">Metrics</TabsTrigger>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
        </TabsList>

        <TabsContent value="metrics" className="space-y-4">
          {/* System Metrics */}
          <Card>
            <CardHeader>
              <CardTitle>System Metrics</CardTitle>
              <CardDescription>
                CPU, Memory, Disk, and Network usage
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {dashboardData.metrics.system.slice(0, 8).map((metric) => (
                  <div key={metric.name} className="border rounded-lg p-4">
                    <h4 className="font-medium text-sm mb-2">
                      {metric.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </h4>
                    <div className="text-2xl font-bold">
                      {formatValue(metric.value, metric.name)}
                    </div>
                    <div className="text-xs text-gray-500">
                      {formatTimestamp(metric.timestamp)}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Application Metrics */}
          <Card>
            <CardHeader>
              <CardTitle>Application Metrics</CardTitle>
              <CardDescription>
                API performance and user activity
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {dashboardData.metrics.application.slice(0, 8).map((metric) => (
                  <div key={metric.name} className="border rounded-lg p-4">
                    <h4 className="font-medium text-sm mb-2">
                      {metric.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </h4>
                    <div className="text-2xl font-bold">
                      {formatValue(metric.value, metric.name)}
                    </div>
                    <div className="text-xs text-gray-500">
                      {formatTimestamp(metric.timestamp)}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Business Metrics */}
          <Card>
            <CardHeader>
              <CardTitle>Business Metrics</CardTitle>
              <CardDescription>
                User growth and engagement
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {dashboardData.metrics.business.slice(0, 8).map((metric) => (
                  <div key={metric.name} className="border rounded-lg p-4">
                    <h4 className="font-medium text-sm mb-2">
                      {metric.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </h4>
                    <div className="text-2xl font-bold">
                      {formatValue(metric.value, metric.name)}
                    </div>
                    <div className="text-xs text-gray-500">
                      {formatTimestamp(metric.timestamp)}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="alerts" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                Active Alerts ({dashboardData.alerts.total_active})
              </CardTitle>
              <CardDescription>
                Current system alerts requiring attention
              </CardDescription>
            </CardHeader>
            <CardContent>
              {dashboardData.alerts.active.length === 0 ? (
                <div className="text-center py-8">
                  <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-500" />
                  <p className="text-gray-600">No active alerts</p>
                  <p className="text-sm text-gray-500">All systems are running normally</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {dashboardData.alerts.active.map((alert) => (
                    <div key={alert.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <Badge className={getAlertLevelColor(alert.level)}>
                            {alert.level.toUpperCase()}
                          </Badge>
                          <h4 className="font-medium">{alert.title}</h4>
                        </div>
                        <span className="text-xs text-gray-500">
                          {formatTimestamp(alert.timestamp)}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{alert.message}</p>
                      <div className="text-xs text-gray-500">
                        Service: {alert.service}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
