import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Plus, ExternalLink, Copy } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import { useAuth } from '../contexts/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function LeadCapture() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [forms, setForms] = useState([]);
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [websites, setWebsites] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [formsRes, leadsRes, websitesRes] = await Promise.all([
        fetch(`${BACKEND_URL}/api/forms`, { credentials: 'include' }),
        fetch(`${BACKEND_URL}/api/leads`, { credentials: 'include' }),
        fetch(`${BACKEND_URL}/api/analyze`, { method: 'GET', credentials: 'include' }).catch(() => ({ ok: false }))
      ]);

      if (formsRes.ok) setForms(await formsRes.json());
      if (leadsRes.ok) setLeads(await leadsRes.json());
      
      setLoading(false);
    } catch (error) {
      console.error('Load error:', error);
      setLoading(false);
    }
  };

  const createForm = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/forms`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          name: 'Contact Form',
          website_id: 'demo-website',
          fields: [
            { name: 'name', type: 'text', required: true },
            { name: 'email', type: 'email', required: true },
            { name: 'message', type: 'textarea', required: true }
          ],
          settings: { autoresponse_enabled: true }
        })
      });

      if (response.ok) {
        toast.success('Form created!');
        setShowCreateDialog(false);
        loadData();
      }
    } catch (error) {
      toast.error('Failed to create form');
    }
  };

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
              <Button variant="ghost" onClick={() => navigate('/analytics')}>Analytics</Button>
              <Button variant="ghost" onClick={logout}>Logout</Button>
            </div>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="font-heading text-3xl font-bold">Lead Capture</h1>
            <p className="text-muted-foreground mt-1">Manage forms and leads</p>
          </div>
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button><Plus className="h-4 w-4 mr-2" />Create Form</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create Lead Capture Form</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <p className="text-sm text-muted-foreground">A default contact form will be created with Name, Email, and Message fields.</p>
                <Button onClick={createForm} className="w-full">Create Contact Form</Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader><CardTitle className="text-sm font-normal text-muted-foreground">Total Forms</CardTitle></CardHeader>
            <CardContent><div className="text-3xl font-bold">{forms.length}</div></CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle className="text-sm font-normal text-muted-foreground">Total Leads</CardTitle></CardHeader>
            <CardContent><div className="text-3xl font-bold">{leads.length}</div></CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle className="text-sm font-normal text-muted-foreground">Hot Leads</CardTitle></CardHeader>
            <CardContent><div className="text-3xl font-bold text-success">{leads.filter(l => l.score === 'hot').length}</div></CardContent>
          </Card>
        </div>

        {loading ? (
          <p>Loading...</p>
        ) : (
          <div className="space-y-8">
            <Card>
              <CardHeader><CardTitle>Recent Leads</CardTitle></CardHeader>
              <CardContent>
                {leads.length === 0 ? (
                  <p className="text-muted-foreground text-center py-8">No leads yet. Create a form and start collecting!</p>
                ) : (
                  <div className="space-y-4">
                    {leads.slice(0, 10).map(lead => (
                      <div key={lead._id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div>
                          <p className="font-medium">{lead.data?.name || 'Anonymous'}</p>
                          <p className="text-sm text-muted-foreground">{lead.data?.email}</p>
                          <p className="text-sm mt-1">{lead.data?.message?.substring(0, 100)}...</p>
                        </div>
                        <div>
                          <Badge variant={lead.score === 'hot' ? 'default' : 'secondary'}>
                            {lead.score}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
