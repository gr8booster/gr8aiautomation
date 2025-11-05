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
  const { isAuthenticated, login, demoLogin, logout, user } = useAuth();
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

    console.log('🔍 Starting analysis, isAuthenticated:', isAuthenticated);
    console.log('🔍 User:', user);

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

      const token = localStorage.getItem('gr8_session_token');
      const headers = { 'Content-Type': 'application/json' };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${BACKEND_URL}/api/analyze`, {
        method: 'POST',
        headers,
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
      const token = localStorage.getItem('gr8_session_token');
      const headers = { 'Content-Type': 'application/json' };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${BACKEND_URL}/api/automations`, {
        method: 'POST',
        headers,
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

      const data = await response.json();
      toast.success(`${recommendation.title} activated!`);
      
      // Redirect to setup wizard
      navigate(`/setup/${data._id}`);
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
            <div className="flex items-center gap-3">
              {isAuthenticated ? (
                <>
                  <Button variant="ghost" onClick={() => navigate('/dashboard')}>Dashboard</Button>
                  <Button variant="ghost" onClick={() => navigate('/billing')}>Billing</Button>
                  <Button variant="outline" onClick={logout}>Logout</Button>
                </>
              ) : (
                <>
                  <Button variant="ghost" onClick={() => navigate('/workforce-scan')}>
                    <Users className="h-4 w-4 mr-1" />
                    Workforce Scan
                  </Button>
                  <Button onClick={() => navigate('/free-audit')} className="bg-yellow-500 hover:bg-yellow-600 text-black font-semibold">
                    Free Audit
                  </Button>
                  <Button variant="outline" onClick={login} data-testid="nav-login-button">
                    Login
                  </Button>
                </>
              )}
            </div>
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
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <Badge className="mb-4 bg-accent text-accent-foreground">
                <Zap className="h-3 w-3 mr-1" /> AI-Powered Automations
              </Badge>
              <h1 className="font-heading text-4xl sm:text-5xl lg:text-6xl tracking-tight leading-[1.05] mb-6">
                Automations from your website — instantly
              </h1>
              <p className="text-base md:text-lg text-muted-foreground max-w-2xl mb-8">
                Paste your URL. We scan your site and propose high-impact automations: chatbots, bookings, lead capture, marketing sequences, and more.
              </p>

              {/* Free Audit CTA */}
              <div className="bg-yellow-50 border-2 border-yellow-400 rounded-xl p-6 mb-8 shadow-lg">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-yellow-400 rounded-full flex items-center justify-center">
                    <Zap className="h-6 w-6 text-black" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-gray-900 mb-2">
                      Get Your Free AI Automation Report
                    </h3>
                    <p className="text-sm text-gray-700 mb-4">
                      Discover what you can automate in 60 seconds. No signup required • 100% Free • Personalized insights
                    </p>
                    <Button 
                      onClick={() => navigate('/free-audit')} 
                      size="lg"
                      className="bg-yellow-500 hover:bg-yellow-600 text-black font-bold shadow-md"
                    >
                      <Sparkles className="h-5 w-5 mr-2" />
                      Generate My Free Report →
                    </Button>
                  </div>
                </div>
              </div>
            </div>

            {/* Hero Image */}
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-tr from-primary/20 to-accent/20 rounded-2xl blur-3xl"></div>
              <img 
                src="/gr8-hero.png" 
                alt="GR8 AI AUTOMATION - AI Agents and Innovation"
                className="relative rounded-2xl shadow-2xl border-2 border-primary/20"
              />
            </div>
          </div>

          {/* URL Input Below Hero */}
          <div className="mt-12 max-w-3xl mx-auto">
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

      {/* Workforce Intelligence Results */}
      {analysis?.workforce && analysis.workforce.workforce_opportunities && analysis.workforce.workforce_opportunities.length > 0 && (
        <section className="py-16 bg-gradient-to-b from-background to-primary/5">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <Badge className="mb-4 bg-primary">🤖 AI Workforce Intelligence</Badge>
              <h2 className="font-heading text-3xl sm:text-4xl font-bold mb-4">
                {analysis.workforce.jobs_found > 0 
                  ? `Replace ${analysis.workforce.jobs_found} Roles with AI Agents`
                  : 'Augment Your Team with AI Agents'
                }
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                {analysis.workforce.summary}
              </p>
              <div className="mt-6 inline-flex items-center gap-4 bg-green-50 border-2 border-green-500 rounded-lg px-6 py-3">
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">
                    ${analysis.workforce.total_potential_savings_monthly?.toLocaleString()}
                  </div>
                  <div className="text-sm text-green-700">Potential Monthly Savings</div>
                </div>
                <div className="text-center border-l-2 border-green-300 pl-4">
                  <div className="text-3xl font-bold text-green-600">
                    ${analysis.workforce.total_potential_savings_annual?.toLocaleString()}
                  </div>
                  <div className="text-sm text-green-700">Annual Savings</div>
                </div>
              </div>
            </div>

            <div className="grid gap-4">
              {analysis.workforce.workforce_opportunities.map((opp, idx) => (
                <Card key={idx} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <Badge className="mb-2" variant={
                          opp.classification === 'Full Replacement' ? 'destructive' :
                          opp.classification === 'Hybrid' ? 'default' : 'secondary'
                        }>
                          {opp.classification}
                        </Badge>
                        <CardTitle className="text-xl">{opp.job_title}</CardTitle>
                        <div className="text-sm text-muted-foreground mt-1">
                          Automation Potential: <strong className="text-primary">{opp.automation_potential}%</strong>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-green-600">
                          ${opp.monthly_savings?.toLocaleString()}
                        </div>
                        <div className="text-xs text-muted-foreground">saved/month</div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm font-semibold mb-2">Recommended AI Agent:</p>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="text-primary border-primary">
                            {opp.ai_agent}
                          </Badge>
                          {opp.secondary_agent && (
                            <Badge variant="outline">
                              + {opp.secondary_agent}
                            </Badge>
                          )}
                        </div>
                      </div>
                      <div>
                        <p className="text-sm font-semibold mb-2">Automated Tasks:</p>
                        <ul className="text-sm space-y-1">
                          {opp.automated_tasks?.slice(0, 3).map((task, i) => (
                            <li key={i} className="flex items-center gap-2">
                              <Check className="h-3 w-3 text-success" />
                              {task}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                    <div className="bg-muted p-3 rounded-lg">
                      <p className="text-sm">{opp.explanation}</p>
                    </div>
                    <Button className="w-full" onClick={() => toast.info('Activate this AI agent from your dashboard!')}>
                      <Zap className="h-4 w-4 mr-2" />
                      Activate {opp.ai_agent}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>
      )}

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


      {/* Trust & Social Proof Section */}
      <section className="py-16 bg-gradient-to-b from-background to-muted/20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="font-heading text-3xl font-bold mb-4">
              Trusted by Businesses Worldwide
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Join thousands of companies automating their workflows with AI
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
            <Card className="text-center">
              <CardContent className="pt-6">
                <img 
                  src="https://images.unsplash.com/photo-1677442136019-21780ecad995" 
                  alt="AI Technology" 
                  className="w-full h-48 object-cover rounded-lg mb-4"
                />
                <h3 className="font-semibold text-lg mb-2">Powered by Advanced AI</h3>
                <p className="text-sm text-muted-foreground">
                  GPT-4 powered intelligence delivers human-like automation at scale
                </p>
              </CardContent>
            </Card>

            <Card className="text-center">
              <CardContent className="pt-6">
                <img 
                  src="https://images.unsplash.com/photo-1522071820081-009f0129c71c" 
                  alt="Team Collaboration" 
                  className="w-full h-48 object-cover rounded-lg mb-4"
                />
                <h3 className="font-semibold text-lg mb-2">Built for Teams</h3>
                <p className="text-sm text-muted-foreground">
                  Collaborate seamlessly with role-based access and shared workflows
                </p>
              </CardContent>
            </Card>

            <Card className="text-center">
              <CardContent className="pt-6">
                <img 
                  src="https://images.unsplash.com/photo-1460925895917-afdab827c52f" 
                  alt="Analytics Dashboard" 
                  className="w-full h-48 object-cover rounded-lg mb-4"
                />
                <h3 className="font-semibold text-lg mb-2">Data-Driven Results</h3>
                <p className="text-sm text-muted-foreground">
                  Track ROI with real-time analytics and performance dashboards
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            <div>
              <div className="text-3xl font-bold text-primary mb-2">7+</div>
              <div className="text-sm text-muted-foreground">AI Agents</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-primary mb-2">98%</div>
              <div className="text-sm text-muted-foreground">Customer Satisfaction</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-primary mb-2">10K+</div>
              <div className="text-sm text-muted-foreground">Automations Deployed</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-primary mb-2">24/7</div>
              <div className="text-sm text-muted-foreground">AI Support</div>
            </div>
          </div>
        </div>
      </section>

      <footer className="border-t border-border py-12 bg-card">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Sparkles className="h-5 w-5 text-primary" />
                <span className="font-heading font-bold">GR8 AI Automation</span>
              </div>
              <p className="text-sm text-muted-foreground">
                AI-powered automations for modern businesses
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold mb-3">Product</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="/free-audit" className="hover:text-primary">Free Audit</a></li>
                <li><a href="/marketplace" className="hover:text-primary">Marketplace</a></li>
                <li><a href="/workflow-builder" className="hover:text-primary">Workflow Builder</a></li>
                <li><a href="/content-generator" className="hover:text-primary">AI Content</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-3">Company</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="/about" className="hover:text-primary">About</a></li>
                <li><a href="/pricing" className="hover:text-primary">Pricing</a></li>
                <li><a href="mailto:support@gr8booster.com" className="hover:text-primary">Contact</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-3">Legal</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="/terms.html" target="_blank" className="hover:text-primary">Terms of Service</a></li>
                <li><a href="/privacy.html" target="_blank" className="hover:text-primary">Privacy Policy</a></li>
              </ul>
            </div>
          </div>
          
          <div className="pt-8 border-t border-border text-center text-sm text-muted-foreground">
            © 2024 GR8 Booster. All rights reserved. Built with AI.
          </div>
        </div>
      </footer>
    </div>
  );
}
