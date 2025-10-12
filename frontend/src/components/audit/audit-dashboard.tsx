'use client';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { DatePickerWithRange } from '@/components/ui/date-picker';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { useQuery } from '@tanstack/react-query';
import { format } from 'date-fns';
import {
  AlertTriangle,
  CheckCircle,
  Download,
  Filter,
  Info,
  Search,
  Shield,
} from 'lucide-react';
import { useEffect, useState } from 'react';
import { DateRange } from 'react-day-picker';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

interface AuditEvent {
  id: string;
  event_type: string;
  user_id: string | null;
  resource_type: string | null;
  resource_id: string | null;
  action: string;
  result: string;
  ip_address: string | null;
  user_agent: string | null;
  event_data: any;
  timestamp: string;
  created_at: string;
}

interface AuditStats {
  total_events: number;
  events_by_type: { [key: string]: number };
  events_by_user: { [key: string]: number };
  events_by_resource: { [key: string]: number };
  events_by_date: { [key: string]: number };
  success_rate: number;
  error_rate: number;
  top_users: Array<{ user_id: string; count: number }>;
  top_resources: Array<{ resource_type: string; count: number }>;
  recent_events: AuditEvent[];
}

interface DashboardData {
  stats: AuditStats;
  chart_data: Array<{ date: string; count: number }>;
  event_type_data: Array<{ name: string; value: number; color: string }>;
  user_activity_data: Array<{ user_id: string; count: number }>;
  resource_activity_data: Array<{ resource_type: string; count: number }>;
  recent_events: AuditEvent[];
  timestamp: string;
}

const fetchAuditDashboard = async (
  startDate?: string,
  endDate?: string
): Promise<DashboardData> => {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);

  const response = await fetch(`/api/audit/dashboard?${params.toString()}`);
  if (!response.ok) {
    throw new Error('Failed to fetch audit dashboard data');
  }
  return response.json();
};

const fetchAuditEvents = async (params: any): Promise<AuditEvent[]> => {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      searchParams.append(key, value.toString());
    }
  });

  const response = await fetch(`/api/audit/events?${searchParams.toString()}`);
  if (!response.ok) {
    throw new Error('Failed to fetch audit events');
  }
  return response.json();
};

const getEventTypeBadge = (eventType: string) => {
  switch (eventType) {
    case 'USER_LOGIN':
    case 'USER_LOGOUT':
      return (
        <Badge className='bg-blue-500 text-white'>
          Auth
        </Badge>
      );
    case 'USER_REGISTRATION':
      return (
        <Badge className='bg-green-500 text-white'>
          Registration
        </Badge>
      );
    case 'DATA_MODIFICATION':
      return (
        <Badge className='bg-yellow-500 text-white'>
          Modification
        </Badge>
      );
    case 'DATA_DELETION':
      return <Badge variant='destructive'>Deletion</Badge>;
    case 'DATA_ACCESS':
      return <Badge variant='secondary'>Access</Badge>;
    case 'ADMIN_ACTION':
      return <Badge variant='destructive'>Admin</Badge>;
    case 'PERMISSION_CHANGE':
      return <Badge variant='destructive'>Permission</Badge>;
    default:
      return <Badge variant='secondary'>{eventType}</Badge>;
  }
};

const getResultBadge = (result: string) => {
  switch (result) {
    case 'success':
      return (
        <Badge className='bg-green-500 text-white'>
          Success
        </Badge>
      );
    case 'failure':
      return <Badge variant='destructive'>Failure</Badge>;
    default:
      return <Badge variant='secondary'>{result}</Badge>;
  }
};

const AuditDashboard = () => {
  const [dateRange, setDateRange] = useState<DateRange | undefined>({
    from: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // 30 days ago
    to: new Date(),
  });

  const [filters, setFilters] = useState({
    event_type: '',
    user_id: '',
    resource_type: '',
    search_query: '',
    limit: 100,
    offset: 0,
  });

  const {
    data: dashboardData,
    isLoading: isDashboardLoading,
    error: dashboardError,
    refetch: refetchDashboard,
  } = useQuery<DashboardData, Error>({
    queryKey: [
      'auditDashboard',
      dateRange?.from?.toISOString(),
      dateRange?.to?.toISOString(),
    ],
    queryFn: () =>
      fetchAuditDashboard(
        dateRange?.from?.toISOString(),
        dateRange?.to?.toISOString()
      ),
    refetchInterval: 30000, // 30 seconds
  });

  const {
    data: auditEvents,
    isLoading: isEventsLoading,
    error: eventsError,
    refetch: refetchEvents,
  } = useQuery<AuditEvent[], Error>({
    queryKey: ['auditEvents', filters],
    queryFn: () => fetchAuditEvents(filters),
    refetchInterval: 30000, // 30 seconds
  });

  useEffect(() => {
    const interval = setInterval(() => {
      refetchDashboard();
      refetchEvents();
    }, 30000); // Refetch every 30 seconds
    return () => clearInterval(interval);
  }, [refetchDashboard, refetchEvents]);

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value, offset: 0 }));
  };

  const handleSearch = () => {
    refetchEvents();
  };

  const handleExport = async () => {
    try {
      const params = new URLSearchParams();
      if (dateRange?.from)
        params.append('start_date', dateRange.from.toISOString());
      if (dateRange?.to) params.append('end_date', dateRange.to.toISOString());
      if (filters.event_type) params.append('event_type', filters.event_type);
      if (filters.user_id) params.append('user_id', filters.user_id);

      const response = await fetch(
        `/api/audit/events/export?${params.toString()}`
      );
      if (!response.ok) throw new Error('Export failed');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit-events-${format(new Date(), 'yyyy-MM-dd')}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  if (isDashboardLoading || isEventsLoading)
    return <div className='text-center py-8'>Loading audit data...</div>;
  if (dashboardError)
    return (
      <div className='text-center py-8 text-red-500'>
        Error: {dashboardError.message}
      </div>
    );
  if (eventsError)
    return (
      <div className='text-center py-8 text-red-500'>
        Error fetching events: {eventsError.message}
      </div>
    );
  if (!dashboardData)
    return <div className='text-center py-8'>No audit data available.</div>;

  const COLORS = [
    '#0088FE',
    '#00C49F',
    '#FFBB28',
    '#FF8042',
    '#8884D8',
    '#82CA9D',
  ];

  return (
    <div className='container mx-auto p-6 bg-gray-50 min-h-screen'>
      <div className='flex justify-between items-center mb-8'>
        <h1 className='text-4xl font-bold text-gray-800 flex items-center'>
          <Shield className='mr-4 text-blue-600' size={40} />
          Audit Dashboard
        </h1>
        <div className='flex space-x-2'>
          <Button onClick={handleExport} variant='outline'>
            <Download className='mr-2' size={16} />
            Export
          </Button>
          <Button
            onClick={() => {
              refetchDashboard();
              refetchEvents();
            }}
            variant='outline'
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card className='mb-6'>
        <CardHeader>
          <CardTitle className='flex items-center'>
            <Filter className='mr-2' size={20} />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4'>
            <div>
              <label className='text-sm font-medium mb-2 block'>
                Date Range
              </label>
              <DatePickerWithRange
                date={dateRange}
                onDateChange={setDateRange}
              />
            </div>
            <div>
              <label className='text-sm font-medium mb-2 block'>
                Event Type
              </label>
              <Select
                value={filters.event_type}
                onValueChange={value => handleFilterChange('event_type', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder='All event types' />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value=''>All event types</SelectItem>
                  <SelectItem value='USER_LOGIN'>User Login</SelectItem>
                  <SelectItem value='USER_LOGOUT'>User Logout</SelectItem>
                  <SelectItem value='USER_REGISTRATION'>
                    User Registration
                  </SelectItem>
                  <SelectItem value='DATA_MODIFICATION'>
                    Data Modification
                  </SelectItem>
                  <SelectItem value='DATA_DELETION'>Data Deletion</SelectItem>
                  <SelectItem value='DATA_ACCESS'>Data Access</SelectItem>
                  <SelectItem value='ADMIN_ACTION'>Admin Action</SelectItem>
                  <SelectItem value='PERMISSION_CHANGE'>
                    Permission Change
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className='text-sm font-medium mb-2 block'>User ID</label>
              <Input
                value={filters.user_id}
                onChange={e => handleFilterChange('user_id', e.target.value)}
                placeholder='Enter user ID'
              />
            </div>
            <div>
              <label className='text-sm font-medium mb-2 block'>
                Resource Type
              </label>
              <Input
                value={filters.resource_type}
                onChange={e =>
                  handleFilterChange('resource_type', e.target.value)
                }
                placeholder='Enter resource type'
              />
            </div>
          </div>
          <div className='flex space-x-2'>
            <Input
              value={filters.search_query}
              onChange={e => handleFilterChange('search_query', e.target.value)}
              placeholder='Search events...'
              className='flex-1'
            />
            <Button onClick={handleSearch}>
              <Search className='mr-2' size={16} />
              Search
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Summary Cards */}
      <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8'>
        <Card className='shadow-lg'>
          <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-2'>
            <CardTitle className='text-sm font-medium'>Total Events</CardTitle>
            <Shield className='h-5 w-5 text-blue-500' />
          </CardHeader>
          <CardContent>
            <div className='text-2xl font-bold'>
              {dashboardData.stats.total_events}
            </div>
            <p className='text-xs text-gray-500'>
              Last updated: {format(new Date(dashboardData.timestamp), 'PPP p')}
            </p>
          </CardContent>
        </Card>

        <Card className='shadow-lg'>
          <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-2'>
            <CardTitle className='text-sm font-medium'>Success Rate</CardTitle>
            <CheckCircle className='h-5 w-5 text-green-500' />
          </CardHeader>
          <CardContent>
            <div className='text-2xl font-bold'>
              {dashboardData.stats.success_rate.toFixed(1)}%
            </div>
            <p className='text-xs text-gray-500'>
              Error rate: {dashboardData.stats.error_rate.toFixed(1)}%
            </p>
          </CardContent>
        </Card>

        <Card className='shadow-lg'>
          <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-2'>
            <CardTitle className='text-sm font-medium'>Active Users</CardTitle>
            <Info className='h-5 w-5 text-purple-500' />
          </CardHeader>
          <CardContent>
            <div className='text-2xl font-bold'>
              {dashboardData.stats.top_users.length}
            </div>
            <p className='text-xs text-gray-500'>
              Most active: {dashboardData.stats.top_users[0]?.user_id || 'N/A'}
            </p>
          </CardContent>
        </Card>

        <Card className='shadow-lg'>
          <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-2'>
            <CardTitle className='text-sm font-medium'>
              Resource Types
            </CardTitle>
            <AlertTriangle className='h-5 w-5 text-orange-500' />
          </CardHeader>
          <CardContent>
            <div className='text-2xl font-bold'>
              {dashboardData.stats.top_resources.length}
            </div>
            <p className='text-xs text-gray-500'>
              Most accessed:{' '}
              {dashboardData.stats.top_resources[0]?.resource_type || 'N/A'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts - Temporarily disabled due to Recharts type issues */}
      {/* TODO: Fix Recharts typing or replace with alternative charting library */}
      <div className='grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8'>
        <Card className='shadow-lg'>
          <CardHeader>
            <CardTitle>Events Over Time</CardTitle>
          </CardHeader>
          <CardContent>
            <p className='text-muted-foreground'>Chart temporarily disabled</p>
          </CardContent>
        </Card>

        <Card className='shadow-lg'>
          <CardHeader>
            <CardTitle>Events by Type</CardTitle>
          </CardHeader>
          <CardContent>
            <p className='text-muted-foreground'>Chart temporarily disabled</p>
          </CardContent>
        </Card>

        <Card className='shadow-lg'>
          <CardHeader>
            <CardTitle>Top Users</CardTitle>
          </CardHeader>
          <CardContent>
            <p className='text-muted-foreground'>Chart temporarily disabled</p>
          </CardContent>
        </Card>

        <Card className='shadow-lg'>
          <CardHeader>
            <CardTitle>Top Resources</CardTitle>
          </CardHeader>
          <CardContent>
            <p className='text-muted-foreground'>Chart temporarily disabled</p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Events */}
      <Card className='shadow-lg'>
        <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-2'>
          <CardTitle className='text-sm font-medium'>
            Recent Audit Events
          </CardTitle>
          <Shield className='h-5 w-5 text-blue-600' />
        </CardHeader>
        <CardContent>
          <ScrollArea className='h-[400px] w-full rounded-md border p-4'>
            {auditEvents && auditEvents.length > 0 ? (
              auditEvents.map((event, index) => (
                <div key={event.id} className='mb-4 last:mb-0'>
                  <div className='flex items-center justify-between mb-2'>
                    <div className='flex items-center space-x-2'>
                      {getEventTypeBadge(event.event_type)}
                      <span className='font-semibold'>{event.action}</span>
                      {getResultBadge(event.result)}
                    </div>
                    <span className='text-xs text-gray-500'>
                      {format(new Date(event.timestamp), 'MMM d, p')}
                    </span>
                  </div>
                  <div className='text-sm text-gray-700 ml-2'>
                    <p>User: {event.user_id || 'Anonymous'}</p>
                    <p>
                      Resource: {event.resource_type}/
                      {event.resource_id || 'N/A'}
                    </p>
                    <p>IP: {event.ip_address || 'N/A'}</p>
                    {event.event_data && (
                      <p>
                        Data:{' '}
                        {JSON.stringify(event.event_data).substring(0, 100)}...
                      </p>
                    )}
                  </div>
                  {index < auditEvents.length - 1 && (
                    <Separator className='my-2' />
                  )}
                </div>
              ))
            ) : (
              <p className='text-gray-500'>No audit events found.</p>
            )}
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
};

export default AuditDashboard;
