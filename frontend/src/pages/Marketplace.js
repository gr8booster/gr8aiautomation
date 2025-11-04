import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Search, Star, Download, Zap, TrendingUp } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import { apiCall } from '../utils/api';
import { useAuth } from '../contexts/AuthContext';

export default function Marketplace() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [templates, setTemplates] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  // Demo templates as fallback
  const demoTemplates = [
    {
      _id: '1',
      name: 'E-commerce Abandoned Cart Recovery',
      description: 'Automatically send personalized emails to customers who abandon their shopping carts',
      category: 'marketing',
      author: 'GR8 AI',
      downloads: 1247,
      rating: 4.8,
      price: 0,
      featured: true
    },
    {
      _id: '2',
      name: 'Customer Onboarding Sequence',
      description: '7-day email sequence to onboard new customers with tips and resources',
      category: 'marketing',
      author: 'GR8 AI',
      downloads: 892,
      rating: 4.9,
      price: 0,
      featured: true
    },
    {
      _id: '3',
      name: 'AI Content Summarizer',
      description: 'Automatically summarize long articles and documents using AI',
      category: 'productivity',
      author: 'Community',
      downloads: 654,
      rating: 4.6,
      price: 9.99,
      featured: false
    },
    {
      _id: '4',
      name: 'Social Media Auto-Poster',
      description: 'Schedule and post to multiple social platforms simultaneously',
      category: 'social',
      author: 'GR8 AI',
      downloads: 2103,
      rating: 4.7,
      price: 0,
      featured: true
    },
    {
      _id: '5',
      name: 'Invoice Payment Reminder',
      description: 'Automated reminders for overdue invoices with escalation',
      category: 'finance',
      author: 'Community',
      downloads: 423,
      rating: 4.5,
      price: 14.99,
      featured: false
    },
    {
      _id: '6',
      name: 'Meeting Scheduler Assistant',
      description: 'AI-powered meeting scheduling with calendar integration',
      category: 'productivity',
      author: 'GR8 AI',
      downloads: 1567,
      rating: 4.9,
      price: 0,
      featured: true
    }
  ];

  const filteredTemplates = templates.filter(t => {
    const matchesSearch = t.name.toLowerCase().includes(search.toLowerCase()) ||
                         t.description.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filter === 'all' || t.category === filter;
    return matchesSearch && matchesFilter;
  });

  const categories = ['all', 'marketing', 'productivity', 'social', 'finance'];

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
              <Button variant="ghost" onClick={() => navigate('/workflow-builder')}>Build Workflow</Button>
              <Button variant="ghost" onClick={logout}>Logout</Button>
            </div>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="font-heading text-3xl font-bold">Automation Marketplace</h1>
          <p className="text-muted-foreground mt-1">Discover and install pre-built automation templates</p>
        </div>

        {/* Search and Filter */}
        <div className="flex flex-col sm:flex-row gap-4 mb-8">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search templates..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10"
            />
          </div>
          <div className="flex gap-2">
            {categories.map(cat => (
              <Button
                key={cat}
                variant={filter === cat ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter(cat)}
                className="capitalize"
              >
                {cat}
              </Button>
            ))}
          </div>
        </div>

        {/* Featured Templates */}
        <div className="mb-6">
          <h2 className="font-semibold text-lg mb-4 flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-primary" />
            Featured Templates
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTemplates.filter(t => t.featured).map(template => (
              <Card key={template._id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <Badge className="mb-2 capitalize">{template.category}</Badge>
                      <CardTitle className="text-lg">{template.name}</CardTitle>
                    </div>
                    <div className="flex items-center gap-1 text-sm">
                      <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                      <span className="font-medium">{template.rating}</span>
                    </div>
                  </div>
                  <CardDescription>{template.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-muted-foreground">
                      <Download className="inline h-3 w-3 mr-1" />
                      {template.downloads.toLocaleString()} installs
                    </div>
                    <div className="text-sm font-semibold">
                      {template.price === 0 ? 'FREE' : `$${template.price}`}
                    </div>
                  </div>
                  <Button onClick={() => installTemplate(template)} className="w-full mt-4">
                    <Zap className="h-4 w-4 mr-2" />
                    Install Template
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* All Templates */}
        <div>
          <h2 className="font-semibold text-lg mb-4">All Templates</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTemplates.filter(t => !t.featured).map(template => (
              <Card key={template._id}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <Badge variant="outline" className="mb-2 capitalize">{template.category}</Badge>
                      <CardTitle className="text-lg">{template.name}</CardTitle>
                    </div>
                    <div className="flex items-center gap-1 text-sm">
                      <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                      <span>{template.rating}</span>
                    </div>
                  </div>
                  <CardDescription>{template.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-sm text-muted-foreground">
                      {template.downloads.toLocaleString()} installs
                    </span>
                    <span className="font-semibold">
                      {template.price === 0 ? 'FREE' : `$${template.price}`}
                    </span>
                  </div>
                  <Button variant="outline" onClick={() => installTemplate(template)} className="w-full">
                    Install
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
