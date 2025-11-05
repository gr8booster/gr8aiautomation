import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Users, Zap, TrendingDown, Check, DollarSign } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '../components/ui/card';
import { Progress } from '../components/ui/progress';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import { apiCall } from '../utils/api';

export default function WorkforceScan() {
  const navigate = useNavigate();
  const [url, setUrl] = useState('');
  const [scanning, setScanning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState(null);

  const handleScan = async () => {
    if (!url) {
      toast.error('Please enter a website URL');
      return;
    }

    setScanning(true);
    setProgress(10);

    try {
      const progressInterval = setInterval(() => {
        setProgress((prev) => Math.min(prev + 15, 85));
      }, 800);

      const response = await apiCall('/api/analyze', {
        method: 'POST',
        body: JSON.stringify({ url: url.trim() })
      });

      clearInterval(progressInterval);

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data = await response.json();
      setProgress(100);
      setResults(data.workforce);
      setScanning(false);
      toast.success('Workforce scan complete!');
    } catch (error) {
      setScanning(false);
      setProgress(0);
      toast.error('Failed to scan. Please try again.');
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
              <Button variant="ghost" onClick={() => navigate('/login')}>Login</Button>
            </div>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-16">
        {!results ? (
          <div className="max-w-3xl mx-auto">
            <div className="text-center mb-12">
              <Badge className="mb-4 bg-primary">
                <Users className="h-3 w-3 mr-1" /> AI Workforce Intelligence
              </Badge>
              <h1 className="font-heading text-4xl sm:text-5xl font-bold mb-6">
                Replace Costly Roles with AI Agents
              </h1>
              <p className="text-lg text-muted-foreground mb-8">
                Discover which positions in your company can be automated or augmented with AI. Save thousands per month while improving efficiency.
              </p>
            </div>

            <Card className="shadow-xl">
              <CardHeader>
                <CardTitle>Scan Your Company Website</CardTitle>
                <CardDescription>We'll analyze your team structure and recommend AI solutions</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Company Website URL</label>
                  <Input
                    type="url"
                    placeholder="https://yourcompany.com"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    disabled={scanning}
                    className="h-12"
                    onKeyPress={(e) => e.key === 'Enter' && handleScan()}
                  />
                </div>

                {scanning && (
                  <div className="space-y-2">
                    <Progress value={progress} className="h-2" />
                    <p className="text-sm text-center text-muted-foreground">
                      {progress < 30 ? 'Scanning website and career pages...' :
                       progress < 60 ? 'Analyzing job roles and functions...' :
                       progress < 90 ? 'Mapping to AI agent capabilities...' :
                       'Calculating cost savings...'}
                    </p>
                  </div>
                )}

                <Button onClick={handleScan} disabled={scanning} className="w-full h-12 text-lg">
                  {scanning ? 'Scanning...' : (
                    <>
                      <Zap className="h-5 w-5 mr-2" />
                      Scan Workforce Opportunities
                    </>
                  )}
                </Button>

                <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t">
                  <div className="text-center">
                    <DollarSign className="h-6 w-6 text-success mx-auto mb-2" />
                    <p className="text-sm text-muted-foreground">Avg $8K+/mo savings</p>
                  </div>
                  <div className="text-center">
                    <TrendingDown className="h-6 w-6 text-success mx-auto mb-2" />
                    <p className="text-sm text-muted-foreground">60-90% cost reduction</p>
                  </div>
                  <div className="text-center">
                    <Zap className="h-6 w-6 text-primary mx-auto mb-2" />
                    <p className="text-sm text-muted-foreground">Deploy in minutes</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        ) : (
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-12">
              <Badge className="mb-4 bg-success">Scan Complete</Badge>
              <h1 className="font-heading text-4xl font-bold mb-4">
                {results.workforce_opportunities?.length || 3} AI Workforce Opportunities Found
              </h1>
              <div className="inline-flex items-center gap-6 bg-green-50 border-2 border-green-500 rounded-lg px-8 py-4">
                <div className="text-center">
                  <div className="text-4xl font-bold text-green-600">
                    ${results.total_potential_savings_monthly?.toLocaleString()}
                  </div>
                  <div className="text-sm text-green-700">Monthly Savings</div>
                </div>
                <div className="text-center border-l-2 border-green-300 pl-6">
                  <div className="text-4xl font-bold text-green-600">
                    ${results.total_potential_savings_annual?.toLocaleString()}
                  </div>
                  <div className="text-sm text-green-700">Annual Savings</div>
                </div>
              </div>
            </div>

            <div className="grid gap-6 mb-8">
              {results.workforce_opportunities?.map((opp, idx) => (
                <Card key={idx} className="hover:shadow-xl transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <Badge className="mb-2" variant={
                          opp.classification === 'Full Replacement' ? 'destructive' :
                          opp.classification === 'Hybrid' ? 'default' : 'secondary'
                        }>
                          {opp.classification}
                        </Badge>
                        <CardTitle className="text-2xl">{opp.job_title}</CardTitle>
                        <div className="text-sm text-muted-foreground mt-2">
                          Automation Potential: <strong className="text-primary text-lg">{opp.automation_potential}%</strong>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-3xl font-bold text-green-600">
                          ${opp.monthly_savings?.toLocaleString()}
                        </div>
                        <div className="text-xs text-muted-foreground">saved/month</div>
                        <div className="text-sm text-muted-foreground mt-1">
                          ${opp.annual_savings?.toLocaleString()}/year
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <p className="text-sm font-semibold mb-3">Recommended AI Solution:</p>
                        <div className="space-y-2">
                          <Badge variant="outline" className="text-primary border-primary text-base px-3 py-1">
                            ⚡ {opp.ai_agent}
                          </Badge>
                          {opp.secondary_agent && (
                            <Badge variant="outline" className="ml-2 text-base px-3 py-1">
                              + {opp.secondary_agent}
                            </Badge>
                          )}
                        </div>
                      </div>
                      <div>
                        <p className="text-sm font-semibold mb-3">Tasks AI Will Handle:</p>
                        <ul className="space-y-2">
                          {opp.automated_tasks?.map((task, i) => (
                            <li key={i} className="flex items-start gap-2">
                              <Check className="h-4 w-4 text-success mt-0.5 flex-shrink-0" />
                              <span className="text-sm">{task}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                    <div className="bg-muted p-4 rounded-lg">
                      <p className="text-sm leading-relaxed">{opp.explanation}</p>
                    </div>
                    <Button className="w-full" size="lg" onClick={() => {
                      toast.success('Sign up to activate this AI agent!');
                      navigate('/login');
                    }}>
                      <Zap className="h-5 w-5 mr-2" />
                      Activate {opp.ai_agent} Now
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>

            <div className="flex gap-4">
              <Button onClick={() => setResults(null)} variant="outline" className="flex-1">
                Scan Another Company
              </Button>
              <Button onClick={() => navigate('/login')} className="flex-1">
                Sign Up to Deploy AI Agents
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
