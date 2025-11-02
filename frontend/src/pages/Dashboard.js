import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Home, Play, Pause, Code, TestTube, Copy, Check } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../components/ui/tabs';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '../components/ui/table';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function Dashboard() {
  const navigate = useNavigate();
  const [automations, setAutomations] = useState([]);
  const [executions, setExecutions] = useState([]);
  const [stats, setStats] = useState({ active: 0, total: 0 });
  const [loading, setLoading] = useState(true);
  const [showCodeDialog, setShowCodeDialog] = useState(false);
  const [selectedAutomation, setSelectedAutomation] = useState(null);
  const [embedCode, setEmbedCode] = useState('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      // Load automations
      const autoResponse = await fetch(`${BACKEND_URL}/api/automations`);
      const autoData = await autoResponse.json();
      setAutomations(autoData);

      // Calculate stats
      const activeCount = autoData.filter(a => a.status === 'active').length;
      setStats({ active: activeCount, total: autoData.length });

      // Load executions
      const execResponse = await fetch(`${BACKEND_URL}/api/executions?limit=20`);
      const execData = await execResponse.json();
      setExecutions(execData);

      setLoading(false);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      toast.error('Failed to load dashboard');
      setLoading(false);
    }
  };

  const toggleAutomationStatus = async (id, currentStatus) => {
    try {
      const newStatus = currentStatus === 'active' ? 'paused' : 'active';
      await fetch(`${BACKEND_URL}/api/automations/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ status: newStatus })
      });

      toast.success(`Automation ${newStatus === 'active' ? 'activated' : 'paused'}`);
      loadData();
    } catch (error) {
      toast.error('Failed to update automation');
    }
  };

  const showEmbedCode = async (automation) => {
    setSelectedAutomation(automation);
    
    // Generate embed code based on automation type
    let code = '';
    if (automation.template_id === 'ai-chatbot') {
      code = `<!-- GR8 AI Chatbot -->
<script src="${window.location.origin}/widget.js"></script>
<script>
  GR8Chatbot.init({
    websiteId: '${automation.website_id}',
    apiUrl: '${BACKEND_URL}'
  });
</script>`;
    } else if (automation.template_id === 'lead-capture') {
      code = `<!-- GR8 Lead Capture Form -->
<div id="gr8-lead-form"></div>
<script src="${window.location.origin}/lead-form-widget.js"></script>
<script>
  GR8LeadForm.init({
    formId: '${automation._id}',
    apiUrl: '${BACKEND_URL}'
  });
</script>`;
    }
    
    setEmbedCode(code);
    setShowCodeDialog(true);
  };

  const copyCode = () => {
    navigator.clipboard.writeText(embedCode);
    setCopied(true);
    toast.success('Code copied to clipboard!');
    setTimeout(() => setCopied(false), 2000);
  };

  const testWidget = (automation) => {
    // Open demo page with the specific automation
    const testUrl = automation.template_id === 'ai-chatbot' 
      ? `${window.location.origin}/demo.html`
      : `${window.location.origin}/demo.html`;
    window.open(testUrl, '_blank');
    toast.success('Test page opened in new tab');
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <Sparkles className="h-6 w-6 text-primary" />
              <span className="font-heading text-xl font-bold">GR8 AI Automation</span>
            </div>
            <Button
              variant="ghost"
              onClick={() => navigate('/')}
              data-testid="nav-home-button"
            >
              <Home className="h-4 w-4 mr-2" />
              Home
            </Button>
          </div>
        </div>
      </header>

      {/* Dashboard Content */}
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground font-normal">Active Automations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-primary">{stats.active}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground font-normal">Total Automations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{stats.total}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground font-normal">Executions (All Time)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{executions.length}</div>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="automations" className="space-y-6">
          <TabsList>
            <TabsTrigger value="automations">Automations</TabsTrigger>
            <TabsTrigger value="executions">Execution History</TabsTrigger>
          </TabsList>

          {/* Automations Tab */}
          <TabsContent value="automations">
            <Card>
              <CardHeader>
                <CardTitle>Your Automations</CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <p className="text-muted-foreground">Loading...</p>
                ) : automations.length === 0 ? (
                  <div className="text-center py-12">
                    <p className="text-muted-foreground mb-4">No automations yet. Analyze a website to get started!</p>
                    <Button onClick={() => navigate('/')}>Analyze Website</Button>
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Created</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {automations.map((automation) => (
                        <TableRow key={automation._id} data-testid="automation-row">
                          <TableCell className="font-medium">{automation.name}</TableCell>
                          <TableCell>
                            <Badge
                              variant={automation.status === 'active' ? 'default' : 'secondary'}
                              className="capitalize"
                            >
                              {automation.status}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-muted-foreground text-sm">
                            {formatDate(automation.created_at)}
                          </TableCell>
                          <TableCell className="text-right space-x-2">
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => toggleAutomationStatus(automation._id, automation.status)}
                              data-testid="automation-toggle-button"
                            >
                              {automation.status === 'active' ? (
                                <Pause className="h-4 w-4" />
                              ) : (
                                <Play className="h-4 w-4" />
                              )}
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Executions Tab */}
          <TabsContent value="executions">
            <Card>
              <CardHeader>
                <CardTitle>Execution History</CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <p className="text-muted-foreground">Loading...</p>
                ) : executions.length === 0 ? (
                  <div className="text-center py-12">
                    <p className="text-muted-foreground">No executions yet.</p>
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Workflow ID</TableHead>
                        <TableHead>State</TableHead>
                        <TableHead>Triggered By</TableHead>
                        <TableHead>Started</TableHead>
                        <TableHead>Duration</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {executions.map((exec) => {
                        const duration = exec.finished_at
                          ? Math.round((new Date(exec.finished_at) - new Date(exec.started_at)) / 1000)
                          : '-';
                        
                        return (
                          <TableRow key={exec._id}>
                            <TableCell className="font-mono text-xs">
                              {exec.workflow_id.substring(0, 8)}...
                            </TableCell>
                            <TableCell>
                              <Badge
                                variant={
                                  exec.state === 'completed' ? 'default' :
                                  exec.state === 'failed' ? 'destructive' :
                                  'secondary'
                                }
                                className="capitalize"
                              >
                                {exec.state}
                              </Badge>
                            </TableCell>
                            <TableCell className="text-sm">{exec.triggered_by}</TableCell>
                            <TableCell className="text-sm text-muted-foreground">
                              {formatDate(exec.started_at)}
                            </TableCell>
                            <TableCell className="text-sm">
                              {typeof duration === 'number' ? `${duration}s` : duration}
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
