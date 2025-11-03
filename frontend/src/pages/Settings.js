import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Mail, Key, Save, Check } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { toast } from 'sonner';
import { apiCall } from '../utils/api';
import { useAuth } from '../contexts/AuthContext';

export default function Settings() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [config, setConfig] = useState({
    sendgrid_api_key: '',
    sender_email: '',
    sender_name: '',
    twilio_account_sid: '',
    twilio_auth_token: '',
    twilio_phone_number: ''
  });
  const [saving, setSaving] = useState(false);
  const [testingEmail, setTestingEmail] = useState(false);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const response = await apiCall('/api/settings/integrations');
      const data = await response.json();
      setConfig({
        sendgrid_api_key: data.sendgrid_configured ? '••••••••' : '',
        sender_email: data.sender_email || '',
        sender_name: data.sender_name || '',
        twilio_account_sid: data.twilio_configured ? '••••••••' : '',
        twilio_auth_token: data.twilio_configured ? '••••••••' : '',
        twilio_phone_number: data.twilio_phone || ''
      });
    } catch (error) {
      console.error('Failed to load config');
    }
  };

  const saveConfig = async () => {
    setSaving(true);
    try {
      await apiCall('/api/settings/integrations', {
        method: 'POST',
        body: JSON.stringify(config)
      });
      toast.success('Settings saved successfully!');
    } catch (error) {
      toast.error('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const testEmail = async () => {
    setTestingEmail(true);
    try {
      await apiCall('/api/settings/test-email', { method: 'POST' });
      toast.success('Test email sent! Check your inbox.');
    } catch (error) {
      toast.error('Failed to send test email');
    } finally {
      setTestingEmail(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
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

      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="font-heading text-3xl font-bold">Integration Settings</h1>
          <p className="text-muted-foreground mt-1">Configure email and SMS services</p>
        </div>

        {/* SendGrid Configuration */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Mail className="h-5 w-5" />
              SendGrid Email Configuration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>SendGrid API Key</Label>
              <Input
                type="password"
                placeholder="SG.xxxxxxxxxxxxx"
                value={config.sendgrid_api_key}
                onChange={(e) => setConfig({...config, sendgrid_api_key: e.target.value})}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Get your API key from <a href="https://app.sendgrid.com/settings/api_keys" target="_blank" className="text-primary hover:underline">SendGrid Dashboard</a>
              </p>
            </div>

            <div>
              <Label>Sender Email</Label>
              <Input
                type="email"
                placeholder="noreply@yourdomain.com"
                value={config.sender_email}
                onChange={(e) => setConfig({...config, sender_email: e.target.value})}
              />
            </div>

            <div>
              <Label>Sender Name</Label>
              <Input
                placeholder="Your Company Name"
                value={config.sender_name}
                onChange={(e) => setConfig({...config, sender_name: e.target.value})}
              />
            </div>

            <div className="flex gap-2">
              <Button onClick={testEmail} disabled={testingEmail} variant="outline" className="flex-1">
                {testingEmail ? 'Sending...' : 'Send Test Email'}
              </Button>
              <Button onClick={saveConfig} disabled={saving} className="flex-1">
                <Save className="h-4 w-4 mr-2" />
                {saving ? 'Saving...' : 'Save Configuration'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Twilio Configuration */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Key className="h-5 w-5" />
              Twilio SMS Configuration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Account SID</Label>
              <Input
                type="password"
                placeholder="ACxxxxxxxxxxxxx"
                value={config.twilio_account_sid}
                onChange={(e) => setConfig({...config, twilio_account_sid: e.target.value})}
              />
            </div>

            <div>
              <Label>Auth Token</Label>
              <Input
                type="password"
                placeholder="Your auth token"
                value={config.twilio_auth_token}
                onChange={(e) => setConfig({...config, twilio_auth_token: e.target.value})}
              />
            </div>

            <div>
              <Label>Phone Number</Label>
              <Input
                placeholder="+1234567890"
                value={config.twilio_phone_number}
                onChange={(e) => setConfig({...config, twilio_phone_number: e.target.value})}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Get a phone number from <a href="https://www.twilio.com/console/phone-numbers" target="_blank" className="text-primary hover:underline">Twilio Console</a>
              </p>
            </div>

            <Button onClick={saveConfig} disabled={saving} className="w-full">
              <Save className="h-4 w-4 mr-2" />
              {saving ? 'Saving...' : 'Save Configuration'}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
