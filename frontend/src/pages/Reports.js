import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, FileText, Download, TrendingUp, Users, Mail } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '../components/ui/table';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import { apiCall } from '../utils/api';
import { useAuth } from '../contexts/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function Reports() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [reports, setReports] = useState([]);
  const [stats, setStats] = useState({ total: 0, hot: 0, conversions: 0 });
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [scoreFilter, setScoreFilter] = useState('');
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    loadReports();
  }, [search, scoreFilter]);

  const loadReports = async () => {
    try {
      let url = '/api/reports?';
      if (search) url += `search=${encodeURIComponent(search)}&`;
      if (scoreFilter) url += `score=${scoreFilter}&`;
      
      const response = await apiCall(url);
      const data = await response.json();
      setReports(Array.isArray(data) ? data : []);

      // Calculate stats
      const hot = data.filter(r => r.automation_score === 'hot').length;
      const conversions = data.filter(r => r.converted === true).length;
      setStats({ total: data.length, hot, conversions });

      setLoading(false);
    } catch (error) {
      console.error('Failed to load reports:', error);
      toast.error('Failed to load reports');
      setLoading(false);
    }
  };

  const exportCSV = async () => {
    setExporting(true);
    try {
      const token = localStorage.getItem('gr8_session_token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/reports/export`, {
        headers: { 'Authorization': `Bearer ${token}` },
        credentials: 'include'
      });
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `automation_reports_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      
      toast.success('Reports exported successfully!');
    } catch (error) {
      toast.error('Failed to export reports');
    } finally {
      setExporting(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  const getScoreBadge = (score) => {
    const variants = {
      hot: 'destructive',
      warm: 'default',
      cold: 'secondary'
    };
    return variants[score] || 'secondary';
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
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
              <Button variant="ghost" onClick={() => navigate('/analytics')}>Analytics</Button>
              <Button variant="ghost" onClick={logout}>Logout</Button>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="font-heading text-3xl font-bold">Automation Reports</h1>
            <p className="text-muted-foreground mt-1">Track generated reports and lead conversions</p>
          </div>
          <Button onClick={exportCSV} disabled={exporting} variant="outline">
            <Download className="h-4 w-4 mr-2" />
            {exporting ? 'Exporting...' : 'Export CSV'}
          </Button>
        </div>

        {/* Search and Filters */}
        <div className="flex gap-4 mb-6">
          <div className="flex-1">
            <Input
              placeholder="Search by email, name, or website..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <select
            value={scoreFilter}
            onChange={(e) => setScoreFilter(e.target.value)}
            className="px-4 py-2 border border-border rounded-md bg-background"
          >
            <option value="">All Scores</option>
            <option value="hot">Hot</option>
            <option value="warm">Warm</option>
            <option value="cold">Cold</option>
          </select>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Reports</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total}</div>
              <p className="text-xs text-muted-foreground">Generated via free audit</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Hot Leads</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-destructive">{stats.hot}</div>
              <p className="text-xs text-muted-foreground">High automation potential</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Conversion Rate</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-success">
                {stats.total > 0 ? Math.round((stats.conversions / stats.total) * 100) : 0}%
              </div>
              <p className="text-xs text-muted-foreground">{stats.conversions} converted to signup</p>
            </CardContent>
          </Card>
        </div>

        {/* Reports Table */}
        <Card>
          <CardHeader>
            <CardTitle>Generated Reports</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <p className="text-muted-foreground">Loading...</p>
            ) : reports.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground mb-4">No reports generated yet</p>
                <Button onClick={() => navigate('/free-audit')}>
                  Create Free Audit Page
                </Button>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Lead</TableHead>
                    <TableHead>Website</TableHead>
                    <TableHead>Score</TableHead>
                    <TableHead>Opportunities</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {reports.map((report) => (
                    <TableRow key={report._id}>
                      <TableCell>
                        <div>
                          <div className="font-medium">{report.lead_name || 'Anonymous'}</div>
                          <div className="text-xs text-muted-foreground flex items-center gap-1">
                            <Mail className="h-3 w-3" />
                            {report.lead_email}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="text-sm">{report.website_url}</TableCell>
                      <TableCell>
                        <Badge variant={getScoreBadge(report.automation_score)} className="capitalize">
                          {report.automation_score}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-center">{report.opportunities_count}</TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {formatDate(report.created_at)}
                      </TableCell>
                      <TableCell>
                        <Badge variant={report.converted ? 'default' : 'secondary'}>
                          {report.converted ? 'Converted' : 'New'}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
