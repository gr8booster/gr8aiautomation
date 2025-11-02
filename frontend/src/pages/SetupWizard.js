import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Sparkles, Check, Code, TestTube, Settings, Zap } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import { apiCall } from '../utils/api';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function SetupWizard() {
  const { automationId } = useParams();
  const navigate = useNavigate();
  const [automation, setAutomation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentStep, setCurrentStep] = useState(1);
  const [config, setConfig] = useState({});
  const [embedCode, setEmbedCode] = useState('');

  useEffect(() => {
    loadAutomation();
  }, [automationId]);

  const loadAutomation = async () => {
    try {
      const response = await apiCall('/api/automations');
      const automations = await response.json();
      const auto = automations.find(a => a._id === automationId);
      
      if (auto) {
        setAutomation(auto);
        generateEmbedCode(auto);
      }
      setLoading(false);
    } catch (error) {
      toast.error('Failed to load automation');
      setLoading(false);
    }
  };

  const generateEmbedCode = (auto) => {
    let code = '';
    
    if (auto.template_id === 'ai-chatbot') {
      code = `<!-- GR8 AI Chatbot -->
<script src="${window.location.origin}/widget.js"></script>
<script>
  GR8Chatbot.init({
    websiteId: '${auto.website_id}',
    apiUrl: '${BACKEND_URL}'
  });
</script>`;
    } else if (auto.template_id === 'lead-capture') {
      code = `<!-- GR8 Lead Capture Form -->
<div id="gr8-lead-form"></div>
<script src="${window.location.origin}/lead-form-widget.js"></script>
<script>
  GR8LeadForm.init({
    formId: '${auto._id}',
    apiUrl: '${BACKEND_URL}'
  });
</script>`;
    }
    
    setEmbedCode(code);
  };

  const copyCode = () => {
    navigator.clipboard.writeText(embedCode);
    toast.success('Code copied to clipboard!');
  };

  const testWidget = () => {
    window.open(`${window.location.origin}/widget-test.html`, '_blank');
    toast.success('Test page opened');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!automation) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-muted-foreground mb-4">Automation not found</p>
          <Button onClick={() => navigate('/dashboard')}>Back to Dashboard</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <Sparkles className="h-6 w-6 text-primary" />
              <span className="font-heading text-xl font-bold">GR8 AI Automation</span>
            </div>
            <Button variant="ghost" onClick={() => navigate('/dashboard')}>
              Back to Dashboard
            </Button>
          </div>
        </div>
      </header>

      {/* Wizard Content */}
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-8">
        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-center gap-4">
            {[1, 2, 3].map((step) => (
              <div key={step} className="flex items-center gap-2">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                  currentStep >= step ? 'bg-primary text-white' : 'bg-muted text-muted-foreground'
                }`}>
                  {currentStep > step ? <Check className="h-5 w-5" /> : step}
                </div>
                {step < 3 && <div className={`w-20 h-1 ${currentStep > step ? 'bg-primary' : 'bg-muted'}`} />}
              </div>
            ))}
          </div>
          <div className="flex items-center justify-center gap-24 mt-2">
            <span className="text-sm">Configure</span>
            <span className="text-sm">Install</span>
            <span className="text-sm">Test</span>
          </div>
        </div>

        {/* Success Banner */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-2">
            <Check className="h-5 w-5 text-green-600" />
            <div>
              <h3 className="font-semibold text-green-900">{automation.name} Activated!</h3>
              <p className="text-sm text-green-700">Complete the setup wizard below to start using your automation.</p>
            </div>
          </div>
        </div>

        {/* Step 1: Configure */}
        {currentStep === 1 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Step 1: Configure Your Automation
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="font-semibold mb-2">Automation Details</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Type:</span>
                    <Badge>{automation.template_id}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Status:</span>
                    <Badge variant={automation.status === 'active' ? 'default' : 'secondary'}>
                      {automation.status}
                    </Badge>
                  </div>
                </div>
              </div>

              {automation.template_id === 'ai-chatbot' && (
                <div className="space-y-4">
                  <h3 className="font-semibold">Chatbot Settings</h3>
                  <div>
                    <Label>Welcome Message</Label>
                    <Input
                      placeholder="Hi! How can I help you today?"
                      value={config.greeting || ''}
                      onChange={(e) => setConfig({...config, greeting: e.target.value})}
                    />
                  </div>
                  <div>
                    <Label>Primary Color</Label>
                    <Input
                      type="color"
                      value={config.primaryColor || '#0c969b'}
                      onChange={(e) => setConfig({...config, primaryColor: e.target.value})}
                    />
                  </div>
                </div>
              )}

              {automation.template_id === 'lead-capture' && (
                <div className="space-y-4">
                  <h3 className="font-semibold">Lead Form Settings</h3>
                  <div>
                    <Label>Form Title</Label>
                    <Input
                      placeholder="Get in Touch"
                      value={config.formTitle || ''}
                      onChange={(e) => setConfig({...config, formTitle: e.target.value})}
                    />
                  </div>
                  <div>
                    <Label>Success Message</Label>
                    <Input
                      placeholder="Thank you! We'll get back to you soon."
                      value={config.successMessage || ''}
                      onChange={(e) => setConfig({...config, successMessage: e.target.value})}
                    />
                  </div>
                </div>
              )}

              <Button onClick={() => setCurrentStep(2)} className="w-full">
                Next: Install Code
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Step 2: Install */}
        {currentStep === 2 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Code className="h-5 w-5" />
                Step 2: Install on Your Website
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="font-semibold mb-2">Installation Instructions</h3>
                <ol className="list-decimal list-inside space-y-2 text-sm text-muted-foreground">
                  <li>Copy the code below</li>
                  <li>Paste it into your website's HTML</li>
                  <li>Add it just before the closing &lt;/body&gt; tag</li>
                  <li>Save and publish your website</li>
                </ol>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <Label>Embed Code</Label>
                  <Button size="sm" variant="outline" onClick={copyCode}>
                    <Code className="h-4 w-4 mr-2" />
                    Copy Code
                  </Button>
                </div>
                <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-xs">
                  <code>{embedCode}</code>
                </pre>
              </div>

              <div className="flex gap-2">
                <Button variant="outline" onClick={() => setCurrentStep(1)} className="flex-1">
                  Back
                </Button>
                <Button onClick={() => setCurrentStep(3)} className="flex-1">
                  Next: Test
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 3: Test */}
        {currentStep === 3 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TestTube className="h-5 w-5" />
                Step 3: Test Your Automation
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="font-semibold mb-2">Test Before Going Live</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Click the button below to open a test page and see your automation in action.
                </p>
                <Button onClick={testWidget} className="w-full" size="lg">
                  <TestTube className="h-5 w-5 mr-2" />
                  Open Test Page
                </Button>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-semibold text-blue-900 mb-2">✨ Your automation is live!</h4>
                <p className="text-sm text-blue-700">
                  Once you've installed the code on your website, the automation will start working immediately.
                  You can monitor performance in the Analytics dashboard.
                </p>
              </div>

              <div className="flex gap-2">
                <Button variant="outline" onClick={() => setCurrentStep(2)} className="flex-1">
                  Back
                </Button>
                <Button onClick={() => navigate('/dashboard')} className="flex-1">
                  <Check className="h-5 w-5 mr-2" />
                  Finish Setup
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
