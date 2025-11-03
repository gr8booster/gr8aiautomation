import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, FileText, Copy, Check, Zap } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Label } from '../components/ui/label';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { toast } from 'sonner';
import { apiCall } from '../utils/api';
import { useAuth } from '../contexts/AuthContext';

export default function ContentGenerator() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [contentType, setContentType] = useState('blog_post');
  const [inputs, setInputs] = useState({
    topic: '',
    tone: 'professional',
    length: '800',
    audience: 'general business audience'
  });
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState(null);
  const [copied, setCopied] = useState(false);

  const contentTypes = [
    { value: 'blog_post', label: 'Blog Post', icon: '📝' },
    { value: 'product_description', label: 'Product Description', icon: '🛍️' },
    { value: 'social_media', label: 'Social Media Posts', icon: '📱' },
    { value: 'email_campaign', label: 'Email Campaign', icon: '📧' },
    { value: 'ad_copy', label: 'Ad Copy', icon: '🎯' }
  ];

  const handleGenerate = async () => {
    if (!inputs.topic) {
      toast.error('Please enter a topic');
      return;
    }

    setGenerating(true);
    try {
      const response = await apiCall('/api/content/generate', {
        method: 'POST',
        body: JSON.stringify({ content_type: contentType, inputs })
      });

      const data = await response.json();
      setResult(data);
      toast.success('Content generated successfully!');
    } catch (error) {
      toast.error('Failed to generate content');
    } finally {
      setGenerating(false);
    }
  };

  const copyContent = () => {
    navigator.clipboard.writeText(result.output);
    setCopied(true);
    toast.success('Content copied to clipboard!');
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
              <Button variant="ghost" onClick={() => navigate('/email-assistant')}>Email Assistant</Button>
              <Button variant="ghost" onClick={logout}>Logout</Button>
            </div>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="font-heading text-3xl font-bold">AI Content Generator</h1>
          <p className="text-muted-foreground mt-1">Create professional content in seconds</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Input Panel */}
          <div className="lg:col-span-1 space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Content Type</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {contentTypes.map(type => (
                    <button
                      key={type.value}
                      onClick={() => setContentType(type.value)}
                      className={`w-full text-left p-3 rounded-lg border-2 transition-colors ${
                        contentType === type.value
                          ? 'border-primary bg-primary/5'
                          : 'border-border hover:border-primary/50'
                      }`}
                    >
                      <span className="text-lg mr-2">{type.icon}</span>
                      <span className="font-medium">{type.label}</span>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Topic/Subject *</Label>
                  <Input
                    value={inputs.topic}
                    onChange={(e) => setInputs({...inputs, topic: e.target.value})}
                    placeholder="What should the content be about?"
                  />
                </div>
                <div>
                  <Label>Tone</Label>
                  <select
                    value={inputs.tone}
                    onChange={(e) => setInputs({...inputs, tone: e.target.value})}
                    className="w-full px-3 py-2 border border-border rounded-md bg-background"
                  >
                    <option value="professional">Professional</option>
                    <option value="casual">Casual</option>
                    <option value="friendly">Friendly</option>
                    <option value="authoritative">Authoritative</option>
                    <option value="enthusiastic">Enthusiastic</option>
                  </select>
                </div>
                <div>
                  <Label>Target Audience</Label>
                  <Input
                    value={inputs.audience}
                    onChange={(e) => setInputs({...inputs, audience: e.target.value})}
                    placeholder="Who is this for?"
                  />
                </div>
                {contentType === 'blog_post' && (
                  <div>
                    <Label>Word Count</Label>
                    <Input
                      type="number"
                      value={inputs.length}
                      onChange={(e) => setInputs({...inputs, length: e.target.value})}
                    />
                  </div>
                )}
                <Button onClick={handleGenerate} disabled={generating} className="w-full">
                  {generating ? 'Generating...' : (
                    <>
                      <Zap className="h-4 w-4 mr-2" />
                      Generate Content
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Output Panel */}
          <div className="lg:col-span-2">
            <Card className="h-full">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Generated Content</CardTitle>
                  {result && (
                    <Button size="sm" variant="outline" onClick={copyContent}>
                      {copied ? (
                        <><Check className="h-4 w-4 mr-1" /> Copied!</>
                      ) : (
                        <><Copy className="h-4 w-4 mr-1" /> Copy</>
                      )}
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {!result ? (
                  <div className="text-center py-12">
                    <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">Your generated content will appear here</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <span>Type: <strong>{contentType.replace('_', ' ').toUpperCase()}</strong></span>
                      <span>Words: <strong>{result.word_count}</strong></span>
                    </div>
                    <div className="bg-muted p-6 rounded-lg max-h-[600px] overflow-y-auto">
                      <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">
                        {result.output}
                      </pre>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
