import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, TrendingUp, Users, Zap, Activity } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '../components/ui/card';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'sonner';
import { apiCall } from '../utils/api';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function Analytics() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState(30);

  useEffect(() => {
    loadAnalytics();
  }, [period]);

  const loadAnalytics = async () => {
    try {
      const [dashResponse, attrResponse] = await Promise.all([
        apiCall(`/api/analytics/dashboard?days=${period}`),
        apiCall(`/api/analytics/attribution?days=${period}`)
      ]);

      if (dashResponse.ok) {
        const data = await dashResponse.json();
        setAnalytics(data);
      }
      
      if (attrResponse.ok) {
        const attrData = await attrResponse.json();
        setAnalytics(prev => ({...prev, attribution: attrData}));
      }
    } catch (error) {
      console.error('Analytics error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/')}>
              <Sparkles className="h-6 w-6 text-primary" />
              <span className="font-heading text-xl font-bold">GR8 AI Automation</span>
            </div>
            <div className="flex items-center gap-4">
              <Button variant="ghost" onClick={() => navigate('/dashboard')}>Dashboard</Button>
              <Button variant="ghost" onClick={() => navigate('/leads')}>Leads</Button>
              <Button variant="ghost" onClick={logout}>Logout</Button>
            </div>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="font-heading text-3xl font-bold">Analytics Dashboard</h1>
            <p className="text-muted-foreground mt-1">Track performance and insights</p>
          </div>
          <select
            value={period}
            onChange={(e) => setPeriod(Number(e.target.value))}
            className="px-4 py-2 border border-border rounded-lg bg-background"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
        </div>

        {analytics && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Automations</CardTitle>
                  <Zap className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{analytics.overview.total_automations}</div>
                  <p className="text-xs text-muted-foreground">{analytics.overview.active_automations} active</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Executions</CardTitle>
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{analytics.overview.total_executions}</div>
                  <p className="text-xs text-success">{analytics.overview.success_rate}% success rate</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Chatbot Messages</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{analytics.chatbot.total_messages}</div>
                  <p className="text-xs text-muted-foreground">{analytics.chatbot.unique_sessions} sessions</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Leads</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{analytics.leads.total_leads}</div>
                  <p className="text-xs text-success">{analytics.leads.hot_leads} hot leads</p>
                </CardContent>
              </Card>
            </div>

            <Card className="mb-8">
              <CardHeader>
                <CardTitle>Activity Over Time</CardTitle>
                <CardDescription>Daily activity metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={analytics.time_series}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="executions" stroke="#0c969b" name="Executions" />
                    <Line type="monotone" dataKey="messages" stroke="#f59e0b" name="Messages" />
                    <Line type="monotone" dataKey="leads" stroke="#10b981" name="Leads" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Chatbot Performance</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Total Messages</span>
                      <span className="font-bold">{analytics.chatbot.total_messages}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Unique Sessions</span>
                      <span className="font-bold">{analytics.chatbot.unique_sessions}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Avg Messages/Session</span>
                      <span className="font-bold">{analytics.chatbot.avg_messages_per_session}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Lead Quality</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Total Leads</span>
                      <span className="font-bold">{analytics.leads.total_leads}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Hot Leads</span>
                      <span className="font-bold text-success">{analytics.leads.hot_leads}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Conversion Rate</span>
                      <span className="font-bold">{analytics.leads.conversion_rate}%</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Lead Attribution */}
            {analytics.attribution && analytics.attribution.length > 0 && (
              <Card className="mt-6">
                <CardHeader>
                  <CardTitle>Lead Attribution (UTM Sources)</CardTitle>
                  <CardDescription>Where your leads are coming from</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {analytics.attribution.map((source, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                        <span className="font-medium capitalize">{source.source}</span>
                        <Badge>{source.leads} leads</Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </>
        )}
      </div>
    </div>
  );
}
