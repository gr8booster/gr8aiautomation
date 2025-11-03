import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Mail, Globe, Zap, Check, TrendingUp, Clock, DollarSign } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Progress } from '../components/ui/progress';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function FreeAudit() {
  const navigate = useNavigate();
  const [url, setUrl] = useState('');
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [report, setReport] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!url || !email) {
      toast.error('Please enter both website URL and email');
      return;
    }

    setIsAnalyzing(true);
    setProgress(10);

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress((prev) => Math.min(prev + 15, 85));
      }, 800);

      const response = await fetch(`${BACKEND_URL}/api/reports/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          url: url.trim(), 
          email: email.trim(),
          name: name.trim() || 'there'
        })
      });

      clearInterval(progressInterval);

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Analysis failed');
      }

      const data = await response.json();
      setProgress(100);
      setReport(data);
      toast.success('Report generated! Check your email.');

    } catch (error) {
      console.error('Analysis error:', error);
      toast.error(error.message || 'Failed to generate report. Please try again.');
      setIsAnalyzing(false);
      setProgress(0);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-background to-accent/5">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/')}>
              <Sparkles className="h-6 w-6 text-primary" />
              <span className="font-heading text-xl font-bold">GR8 AI Automation</span>
            </div>
            <Button variant="ghost" onClick={() => navigate('/login')}>
              Login
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <Badge className="mb-4 bg-primary/10 text-primary">
            <Zap className="h-3 w-3 mr-1" /> 100% Free • No Credit Card
          </Badge>
          <h1 className="font-heading text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight mb-6">
            Discover What You Can <span className="text-primary">Automate</span><br />in 60 Seconds
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-8">
            Get a personalized AI-powered automation report for your website. Discover opportunities to save time, reduce costs, and grow revenue with intelligent automation.
          </p>
        </div>

        {!report ? (
          <div className="max-w-2xl mx-auto">
            {/* Main Form */}
            <Card className="shadow-xl">
              <CardHeader>
                <CardTitle className="text-center">Get Your Free Automation Report</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      <Globe className="inline h-4 w-4 mr-1" />
                      Your Website URL *
                    </label>
                    <Input
                      type="url"
                      placeholder="https://yourwebsite.com"
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      disabled={isAnalyzing}
                      required
                      className="h-12"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">
                      <Mail className="inline h-4 w-4 mr-1" />
                      Business Email *
                    </label>
                    <Input
                      type="email"
                      placeholder="you@company.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      disabled={isAnalyzing}
                      required
                      className="h-12"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Name (Optional)
                    </label>
                    <Input
                      type="text"
                      placeholder="John Doe"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      disabled={isAnalyzing}
                      className="h-12"
                    />
                  </div>

                  {isAnalyzing && (
                    <div className="space-y-2">
                      <Progress value={progress} className="h-2" />
                      <p className="text-sm text-center text-muted-foreground">
                        {progress < 30 ? 'Scanning your website...' :
                         progress < 60 ? 'Analyzing automation opportunities...' :
                         progress < 90 ? 'Generating your personalized report...' :
                         'Finalizing report...'}
                      </p>
                    </div>
                  )}

                  <Button 
                    type="submit" 
                    className="w-full h-12 text-lg"
                    disabled={isAnalyzing}
                  >
                    {isAnalyzing ? 'Generating Report...' : 'Generate My Free Report'}
                  </Button>

                  <p className="text-xs text-center text-muted-foreground">
                    🔒 Your data is secure. We'll never spam you or share your information.
                  </p>
                </form>
              </CardContent>
            </Card>

            {/* Trust Elements */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
              <div className="text-center">
                <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Clock className="h-6 w-6 text-primary" />
                </div>
                <h3 className="font-semibold mb-1">60-Second Analysis</h3>
                <p className="text-sm text-muted-foreground">AI scans your entire site instantly</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-3">
                  <TrendingUp className="h-6 w-6 text-primary" />
                </div>
                <h3 className="font-semibold mb-1">Personalized Insights</h3>
                <p className="text-sm text-muted-foreground">Custom recommendations for your business</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-3">
                  <DollarSign className="h-6 w-6 text-primary" />
                </div>
                <h3 className="font-semibold mb-1">ROI Estimates</h3>
                <p className="text-sm text-muted-foreground">See potential savings and revenue</p>
              </div>
            </div>
          </div>
        ) : (
          /* Report Preview */
          <div className="max-w-3xl mx-auto">
            <Card className="shadow-xl">
              <CardHeader className="bg-gradient-to-r from-primary/10 to-accent/10">
                <div className="text-center">
                  <Badge className="mb-2">Report Generated</Badge>
                  <CardTitle className="text-2xl">Your AI Automation Report is Ready!</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="pt-6 space-y-6">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <Check className="h-5 w-5 text-green-600 mt-0.5" />
                    <div>
                      <h3 className="font-semibold text-green-900 mb-1">Report Sent to Your Email!</h3>
                      <p className="text-sm text-green-700">
                        We've sent your complete automation report to <strong>{email}</strong>
                      </p>
                    </div>
                  </div>
                </div>

                {/* Quick Summary */}
                <div>
                  <h3 className="font-semibold mb-3">Quick Summary</h3>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                      <span className="text-sm">Automation Opportunities</span>
                      <Badge>{report.opportunities_count || 5}</Badge>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                      <span className="text-sm">Automation Score</span>
                      <Badge variant={report.score === 'hot' ? 'default' : 'secondary'}>
                        {report.score || 'High'}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                      <span className="text-sm">Estimated Monthly Savings</span>
                      <span className="font-semibold text-primary">${report.estimated_savings || 5000}</span>
                    </div>
                  </div>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-900 mb-2">📧 Check Your Email</h4>
                  <p className="text-sm text-blue-700 mb-3">
                    Your full PDF report includes:
                  </p>
                  <ul className="text-sm text-blue-700 space-y-1">
                    <li>✓ Detailed automation opportunities by category</li>
                    <li>✓ ROI estimates for each recommendation</li>
                    <li>✓ Implementation roadmap</li>
                    <li>✓ Next steps to get started</li>
                  </ul>
                </div>

                <div className="flex gap-3">
                  <Button onClick={() => navigate('/login')} className="flex-1">
                    <Zap className="h-4 w-4 mr-2" />
                    Start Automating Now
                  </Button>
                  <Button variant="outline" onClick={() => window.location.reload()} className="flex-1">
                    Generate Another Report
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
