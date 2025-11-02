import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Check, Zap, CreditCard } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const plans = [
  {
    id: 'free',
    name: 'Free',
    price: 0,
    features: [
      '1 website',
      '3 automations',
      '100 AI interactions/month',
      'Community support'
    ]
  },
  {
    id: 'starter',
    name: 'Starter',
    price: 29,
    features: [
      '3 websites',
      '10 automations',
      '1,000 AI interactions/month',
      'Email support',
      'Remove GR8 branding'
    ],
    popular: true
  },
  {
    id: 'pro',
    name: 'Pro',
    price: 99,
    features: [
      '10 websites',
      'Unlimited automations',
      '10,000 AI interactions/month',
      'Priority support',
      'Custom branding',
      'Advanced analytics'
    ]
  }
];

export default function Billing() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [currentPlan, setCurrentPlan] = useState('free');
  const [usage, setUsage] = useState(null);
  const [loading, setLoading] = useState({});

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/me`, {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setCurrentPlan(data.user.plan || 'free');
        setUsage(data.usage);
      }
    } catch (error) {
      console.error('Failed to load user data:', error);
    }
  };

  const handleUpgrade = async (planId) => {
    if (planId === 'free') return;
    
    setLoading({ [planId]: true });
    try {
      const response = await fetch(`${BACKEND_URL}/api/billing/checkout?plan_id=${planId}`, {
        method: 'POST',
        headers: {
          'Origin': window.location.origin
        },
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        window.location.href = data.url;
      } else {
        toast.error('Failed to create checkout session');
      }
    } catch (error) {
      console.error('Checkout error:', error);
      toast.error('Checkout failed');
    } finally {
      setLoading({ [planId]: false });
    }
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
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <Badge className="mb-4 bg-accent text-accent-foreground">
            <Zap className="h-3 w-3 mr-1" /> Pricing Plans
          </Badge>
          <h1 className="font-heading text-4xl sm:text-5xl font-bold mb-4">
            Choose Your Plan
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Upgrade to unlock more automations, AI interactions, and premium features.
          </p>
        </div>

        {/* Current Usage */}
        {usage && (
          <Card className="mb-8 max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle className="text-lg">Current Usage (This Month)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">AI Interactions</p>
                  <p className="text-2xl font-bold">{usage.ai_interactions || 0}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Chatbot Messages</p>
                  <p className="text-2xl font-bold">{usage.chatbot_messages || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Plans */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((plan) => {
            const isCurrent = plan.id === currentPlan;
            const isUpgrade = plans.findIndex(p => p.id === currentPlan) < plans.findIndex(p => p.id === plan.id);
            
            return (
              <Card
                key={plan.id}
                className={`relative ${plan.popular ? 'border-primary shadow-lg' : ''} ${isCurrent ? 'bg-accent/10' : ''}`}
              >
                {plan.popular && (
                  <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-primary-foreground">
                    Most Popular
                  </Badge>
                )}
                <CardHeader>
                  <CardTitle className="text-2xl">{plan.name}</CardTitle>
                  <CardDescription>
                    <span className="text-4xl font-bold text-foreground">${plan.price}</span>
                    {plan.price > 0 && <span className="text-muted-foreground">/month</span>}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {plan.features.map((feature, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <Check className="h-5 w-5 text-success mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
                <CardFooter>
                  {isCurrent ? (
                    <Button className="w-full" disabled>
                      Current Plan
                    </Button>
                  ) : isUpgrade ? (
                    <Button
                      className="w-full"
                      onClick={() => handleUpgrade(plan.id)}
                      disabled={loading[plan.id]}
                    >
                      <CreditCard className="h-4 w-4 mr-2" />
                      {loading[plan.id] ? 'Processing...' : 'Upgrade'}
                    </Button>
                  ) : (
                    <Button className="w-full" variant="outline" disabled>
                      Downgrade (Contact Support)
                    </Button>
                  )}
                </CardFooter>
              </Card>
            );
          })}
        </div>

        {/* FAQ */}
        <div className="mt-16 max-w-3xl mx-auto">
          <h2 className="font-heading text-2xl font-bold mb-6 text-center">Frequently Asked Questions</h2>
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Can I change plans anytime?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Yes! You can upgrade your plan at any time. Downgrades will take effect at the end of your billing period.
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-base">What happens if I exceed my limits?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  You'll be notified when approaching limits. Automations will continue to work but new activations will require an upgrade.
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Is there a free trial for paid plans?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  The Free plan is your trial! Upgrade anytime when you're ready for more features.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
