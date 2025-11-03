import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Mail, Send, Copy, Check, Wand2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Label } from '../components/ui/label';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../components/ui/tabs';
import { toast } from 'sonner';
import { apiCall } from '../utils/api';
import { useAuth } from '../contexts/AuthContext';

export default function EmailAssistant() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [activeTab, setActiveTab] = useState('draft');
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState(null);
  const [copied, setCopied] = useState(false);

  // Draft Response State
  const [draftInputs, setDraftInputs] = useState({
    original_email: '',
    tone: 'professional and friendly',
    key_points: '',
    recipient_name: ''
  });

  // Campaign State
  const [campaignInputs, setCampaignInputs] = useState({
    topic: '',
    goal: 'Generate interest and drive action',
    audience: 'Business professionals',
    tone: 'professional yet engaging',
    num_variations: 2
  });

  const handleDraft = async () => {
    if (!draftInputs.original_email) {
      toast.error('Please paste the original email');
      return;
    }

    setGenerating(true);
    try {
      const response = await apiCall('/api/email/draft', {
        method: 'POST',
        body: JSON.stringify(draftInputs)
      });

      const data = await response.json();
      setResult(data.draft);
      toast.success('Email draft generated!');
    } catch (error) {
      toast.error('Failed to generate draft');
    } finally {
      setGenerating(false);
    }
  };

  const handleCampaign = async () => {
    if (!campaignInputs.topic) {
      toast.error('Please enter a campaign topic');
      return;
    }

    setGenerating(true);
    try {
      const response = await apiCall('/api/email/campaign', {
        method: 'POST',
        body: JSON.stringify(campaignInputs)
      });

      const data = await response.json();
      setResult(data.variations);
      toast.success('Email campaign generated!');
    } catch (error) {
      toast.error('Failed to generate campaign');
    } finally {
      setGenerating(false);
    }
  };

  const copyContent = () => {
    navigator.clipboard.writeText(result);
    setCopied(true);
    toast.success('Copied to clipboard!');
    setTimeout(() => setCopied(false), 2000);
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
              <Button variant="ghost" onClick={() => navigate('/content-generator')}>Content Generator</Button>
              <Button variant="ghost" onClick={logout}>Logout</Button>
            </div>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="font-heading text-3xl font-bold">AI Email Assistant</h1>
          <p className="text-muted-foreground mt-1">Draft responses and create campaigns instantly</p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList>
            <TabsTrigger value="draft">Draft Response</TabsTrigger>
            <TabsTrigger value="campaign">Create Campaign</TabsTrigger>
          </TabsList>

          {/* Draft Response Tab */}
          <TabsContent value="draft">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Email to Respond To</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label>Paste Original Email *</Label>
                    <Textarea
                      rows={8}
                      value={draftInputs.original_email}
                      onChange={(e) => setDraftInputs({...draftInputs, original_email: e.target.value})}
                      placeholder="Paste the email you need to respond to..."
                    />
                  </div>
                  <div>
                    <Label>Recipient Name</Label>
                    <Input
                      value={draftInputs.recipient_name}
                      onChange={(e) => setDraftInputs({...draftInputs, recipient_name: e.target.value})}
                      placeholder="John, Sarah, etc."
                    />
                  </div>
                  <div>
                    <Label>Tone</Label>
                    <Input
                      value={draftInputs.tone}
                      onChange={(e) => setDraftInputs({...draftInputs, tone: e.target.value})}
                      placeholder="professional and friendly"
                    />
                  </div>
                  <div>
                    <Label>Key Points to Address</Label>
                    <Textarea
                      rows={3}
                      value={draftInputs.key_points}
                      onChange={(e) => setDraftInputs({...draftInputs, key_points: e.target.value})}
                      placeholder="What should the response cover?"
                    />
                  </div>
                  <Button onClick={handleDraft} disabled={generating} className="w-full">
                    {generating ? 'Generating...' : (
                      <><Wand2 className="h-4 w-4 mr-2" /> Generate Response</>
                    )}
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>AI-Generated Response</CardTitle>
                    {result && (
                      <Button size="sm" variant="outline" onClick={copyContent}>
                        {copied ? <><Check className="h-4 w-4 mr-1" /> Copied!</> : <><Copy className="h-4 w-4 mr-1" /> Copy</>}
                      </Button>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  {!result ? (
                    <div className="text-center py-12">
                      <Mail className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                      <p className="text-muted-foreground">Your draft will appear here</p>
                    </div>
                  ) : (
                    <div className="bg-muted p-4 rounded-lg max-h-[500px] overflow-y-auto">
                      <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">{result}</pre>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Campaign Tab */}
          <TabsContent value="campaign">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Campaign Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label>Campaign Topic *</Label>
                    <Input
                      value={campaignInputs.topic}
                      onChange={(e) => setCampaignInputs({...campaignInputs, topic: e.target.value})}
                      placeholder="Product launch, sale, update, etc."
                    />
                  </div>
                  <div>
                    <Label>Goal</Label>
                    <Input
                      value={campaignInputs.goal}
                      onChange={(e) => setCampaignInputs({...campaignInputs, goal: e.target.value})}
                      placeholder="Drive sales, get signups, etc."
                    />
                  </div>
                  <div>
                    <Label>Target Audience</Label>
                    <Input
                      value={campaignInputs.audience}
                      onChange={(e) => setCampaignInputs({...campaignInputs, audience: e.target.value})}
                    />
                  </div>
                  <div>
                    <Label>Tone</Label>
                    <Input
                      value={campaignInputs.tone}
                      onChange={(e) => setCampaignInputs({...campaignInputs, tone: e.target.value})}
                    />
                  </div>
                  <div>
                    <Label>Number of Variations</Label>
                    <Input
                      type="number"
                      min="1"
                      max="5"
                      value={campaignInputs.num_variations}
                      onChange={(e) => setCampaignInputs({...campaignInputs, num_variations: parseInt(e.target.value)})}
                    />
                  </div>
                  <Button onClick={handleCampaign} disabled={generating} className="w-full">
                    {generating ? 'Generating...' : (
                      <><Wand2 className="h-4 w-4 mr-2" /> Generate Campaign</>
                    )}
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Campaign Variations</CardTitle>
                    {result && (
                      <Button size="sm" variant="outline" onClick={copyContent}>
                        {copied ? <><Check className="h-4 w-4 mr-1" /> Copied!</> : <><Copy className="h-4 w-4 mr-1" /> Copy All</>}
                      </Button>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  {!result ? (
                    <div className="text-center py-12">
                      <Send className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                      <p className="text-muted-foreground">Campaign variations will appear here</p>
                    </div>
                  ) : (
                    <div className="bg-muted p-4 rounded-lg max-h-[500px] overflow-y-auto">
                      <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">{result}</pre>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
