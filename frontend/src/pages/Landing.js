import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, useScroll, useTransform } from 'framer-motion';
import { Sparkles, Zap, Bot, Calendar, Mail, BarChart3, Globe, ArrowRight, Check } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Progress } from '../components/ui/progress';
import { Card, CardHeader, CardContent, CardTitle, CardDescription } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import { useAuth } from '../contexts/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function Landing() {
  const navigate = useNavigate();
  const { isAuthenticated, login, logout, user } = useAuth();
  const [url, setUrl] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [analysis, setAnalysis] = useState(null);

  const { scrollY } = useScroll();
  const y = useTransform(scrollY, [0, 300], [0, -40]);

  const startAnalysis = async () => {
    if (!url || !url.trim()) {
      toast.error('Please enter a valid website URL');
      return;
    }

    // Check if authenticated
    if (!isAuthenticated) {
      toast.error('Please login to analyze websites');
      login();
      return;
    }

    setIsAnalyzing(true);
    setProgress(10);

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress((prev) => Math.min(prev + 15, 85));
      }, 500);

      const response = await fetch(`${BACKEND_URL}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ url: url.trim() })
      });

      clearInterval(progressInterval);

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Analysis failed');
      }

      const data = await response.json();
      setProgress(100);
      setAnalysis(data);
      toast.success('Analysis complete!');

    } catch (error) {
      console.error('Analysis error:', error);
      toast.error(error.message || 'Failed to analyze website. Please try again.');
      setIsAnalyzing(false);
      setProgress(0);
    }
  };

  const activateAutomation = async (recommendation) => {
    if (!isAuthenticated) {
      toast.error('Please login to activate automations');
      login();
      return;
    }

    try {
      const response = await fetch(`${BACKEND_URL}/api/automations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          website_id: analysis.analysis_id,
          recommendation_key: recommendation.key,
          config: {}
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Activation failed');
      }

      toast.success(`${recommendation.title} activated!`);
      setTimeout(() => navigate('/dashboard'), 1500);
    } catch (error) {
      console.error('Activation error:', error);
      toast.error(error.message || 'Failed to activate automation');
    }
  };

  return (
    <div className="min-h-screen">
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
              onClick={() => navigate('/dashboard')}
              data-testid="nav-dashboard-button"
            >
              Dashboard
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <motion.div
          style={{ y }}
          className="absolute inset-0 pointer-events-none bg-[radial-gradient(120%_120%_at_0%_0%,hsl(169_53%_82%)_0%,hsl(190_72%_35%/0.10)_40%,hsl(40_42%_88%)_100%)]"
        />
        <div className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
          <div className="max-w-3xl">
            <Badge className="mb-4 bg-accent text-accent-foreground">
              <Zap className="h-3 w-3 mr-1" /> AI-Powered Automations
            </Badge>
            <h1 className="font-heading text-4xl sm:text-5xl lg:text-6xl tracking-tight leading-[1.05] mb-6">
              Automations from your website — instantly
            </h1>
            <p className="text-base md:text-lg text-muted-foreground max-w-2xl mb-8">
              Paste your URL. We scan your site and propose high-impact automations: chatbots, bookings, lead capture, marketing sequences, and more.
            </p>

            {/* URL Input */}
            <div className="flex flex-col sm:flex-row gap-3 mb-6">
              <Input
                data-testid="hero-url-input"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && startAnalysis()}
                placeholder="https://yourdomain.com"
                className="h-12 sm:min-w-[400px] bg-background"
                disabled={isAnalyzing}
              />
              <Button
                data-testid="hero-analyze-button"
                onClick={startAnalysis}
                disabled={isAnalyzing}
                className="h-12 px-8 transition-colors duration-300"
              >
                {isAnalyzing ? 'Analyzing...' : 'Analyze URL'}
              </Button>
            </div>

            {/* Progress */}
            {isAnalyzing && (
              <div className="space-y-2 animate-in fade-in duration-500">
                <Progress data-testid="hero-analysis-progress" value={progress} className="h-2" />
                <p className="text-sm text-muted-foreground">
                  {progress < 30 && 'Fetching website...'}
                  {progress >= 30 && progress < 60 && 'Extracting content...'}
                  {progress >= 60 && progress < 90 && 'AI analyzing patterns...'}
                  {progress >= 90 && 'Generating recommendations...'}
                </p>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Analysis Results */}
      {analysis && (
        <section className="py-16 bg-muted/30">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="mb-12">
              <h2 className="font-heading text-3xl sm:text-4xl font-bold mb-4">
                AI Analysis Complete
              </h2>
              <p className="text-lg text-muted-foreground mb-2">{analysis.summary}</p>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Check className="h-4 w-4 text-success" />
                Business Type: <span className="font-medium">{analysis.business_type}</span>
                <span className="mx-2">•</span>
                Confidence: <span className="font-medium">{Math.round(analysis.confidence_score * 100)}%</span>
              </div>
            </div>

            {/* Recommendations Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {analysis.recommendations.map((rec, idx) => (
                <motion.div
                  key={rec.key}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.1 }}
                >
                  <Card
                    data-testid="automation-recommendation-card"
                    className="h-full hover:shadow-lg transition-shadow duration-300 border-muted"
                  >
                    <CardHeader>
                      <div className="flex items-start justify-between mb-2">
                        <div className="p-2 bg-primary/10 rounded-lg">
                          {rec.category === 'agent' && <Bot className="h-5 w-5 text-primary" />}
                          {rec.category === 'booking' && <Calendar className="h-5 w-5 text-primary" />}
                          {rec.category === 'marketing' && <Mail className="h-5 w-5 text-primary" />}
                          {rec.category === 'lead_generation' && <Zap className="h-5 w-5 text-primary" />}
                          {rec.category === 'analytics' && <BarChart3 className="h-5 w-5 text-primary" />}
                          {rec.category === 'social_media' && <Globe className="h-5 w-5 text-primary" />}
                        </div>
                        <Badge
                          variant={rec.priority === 'high' ? 'default' : 'secondary'}
                          className="text-xs"
                        >
                          {rec.priority}
                        </Badge>
                      </div>
                      <CardTitle className="text-lg">{rec.title}</CardTitle>
                      <CardDescription className="text-sm">{rec.description}</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">Why you need this:</p>
                        <p className="text-sm">{rec.rationale}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">Expected impact:</p>
                        <p className="text-sm font-medium text-success">{rec.expected_impact}</p>
                      </div>
                      <Button
                        data-testid="automation-deploy-button"
                        onClick={() => activateAutomation(rec)}
                        className="w-full transition-colors duration-300"
                      >
                        Activate <ArrowRight className="h-4 w-4 ml-2" />
                      </Button>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Features Section */}
      {!analysis && (
        <section className="py-20 bg-muted/30">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="font-heading text-3xl sm:text-4xl font-bold mb-4">
                Launch automations in minutes, not months
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                No coding required. AI analyzes your website and builds custom automations tailored to your business.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                {
                  icon: <Bot className="h-8 w-8 text-primary" />,
                  title: '24/7 AI Agents',
                  description: 'Intelligent chatbots that handle support, qualify leads, and engage visitors.'
                },
                {
                  icon: <Calendar className="h-8 w-8 text-primary" />,
                  title: 'Smart Scheduling',
                  description: 'Automated booking systems with calendar sync and email confirmations.'
                },
                {
                  icon: <Zap className="h-8 w-8 text-primary" />,
                  title: 'Lead Generation',
                  description: 'Capture and nurture leads with AI-powered forms and follow-ups.'
                }
              ].map((feature, idx) => (
                <Card key={idx} className="border-muted">
                  <CardHeader>
                    <div className="mb-3">{feature.icon}</div>
                    <CardTitle className="text-xl">{feature.title}</CardTitle>
                    <CardDescription>{feature.description}</CardDescription>
                  </CardHeader>
                </Card>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="border-t border-border py-12 bg-card">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              <span className="font-heading font-bold">GR8 AI Automation</span>
            </div>
            <p className="text-sm text-muted-foreground">
              © 2025 GR8 AI Automation. Launch-ready automations.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
