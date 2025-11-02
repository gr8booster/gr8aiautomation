import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Sparkles, Copy, Check } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/card';
import { toast } from 'sonner';
import { useAuth } from '../contexts/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function ChatbotSetup() {
  const navigate = useNavigate();
  const { automationId } = useParams();
  const { logout } = useAuth();
  const [widgetCode, setWidgetCode] = useState('');
  const [copied, setCopied] = useState(false);
  const [websiteId, setWebsiteId] = useState('');

  useEffect(() => {
    loadWidgetCode();
  }, [automationId]);

  const loadWidgetCode = async () => {
    try {
      // Get automation details
      const autoResponse = await fetch(`${BACKEND_URL}/api/automations`, {
        credentials: 'include'
      });
      
      if (autoResponse.ok) {
        const automations = await autoResponse.json();
        const automation = automations.find(a => a._id === automationId);
        
        if (automation) {
          setWebsiteId(automation.website_id);
          
          // Get widget code
          const widgetResponse = await fetch(`${BACKEND_URL}/api/chatbot/widget/${automation.website_id}`, {
            credentials: 'include'
          });
          
          if (widgetResponse.ok) {
            const data = await widgetResponse.json();
            setWidgetCode(data.widget_code);
          }
        }
      }
    } catch (error) {
      console.error('Failed to load widget code:', error);
      toast.error('Failed to load widget code');
    }
  };

  const copyCode = () => {
    navigator.clipboard.writeText(widgetCode);
    setCopied(true);
    toast.success('Widget code copied!');
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen">
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
              <Button variant="ghost" onClick={logout}>Logout</Button>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="font-heading text-4xl font-bold mb-4">AI Chatbot Setup</h1>
        <p className="text-lg text-muted-foreground mb-8">
          Follow these steps to add the AI chatbot to your website.
        </p>

        {/* Installation Steps */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Step 1: Copy the Widget Code</CardTitle>
              <CardDescription>
                Copy this code snippet and paste it into your website's HTML, just before the closing &lt;/body&gt; tag.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="relative">
                <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-sm">
                  <code>{widgetCode || 'Loading...'}</code>
                </pre>
                <Button
                  size="sm"
                  className="absolute top-2 right-2"
                  onClick={copyCode}
                  disabled={!widgetCode}
                >
                  {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                  {copied ? 'Copied!' : 'Copy'}
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Step 2: Customize (Optional)</CardTitle>
              <CardDescription>
                The chatbot will automatically match your website's style. You can customize colors and position in the dashboard.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Step 3: Test Your Chatbot</CardTitle>
              <CardDescription>
                Once installed, visit your website and the chatbot widget will appear in the bottom right corner.
              </CardDescription>
            </CardHeader>
          </Card>
        </div>

        {/* Actions */}
        <div className="mt-8 flex gap-4">
          <Button onClick={() => navigate('/dashboard')}>
            Back to Dashboard
          </Button>
          <Button variant="outline" onClick={() => window.open('https://docs.gr8ai.com/chatbot', '_blank')}>
            View Documentation
          </Button>
        </div>
      </div>
    </div>
  );
}
