import React, { useState, useEffect } from 'react';
import { X, Sparkles } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { useNavigate } from 'react-router-dom';

export default function FreeAuditPopup() {
  const navigate = useNavigate();
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    // Don't show popup on login, signup, or free-audit pages
    const excludedPages = ['/login', '/free-audit'];
    if (excludedPages.includes(location.pathname)) {
      return;
    }

    // Show popup after 10 seconds if not dismissed
    const wasDismissed = localStorage.getItem('audit_popup_dismissed');
    if (wasDismissed) {
      setDismissed(true);
      return;
    }

    const timer = setTimeout(() => {
      setIsOpen(true);
    }, 10000);

    return () => clearTimeout(timer);
  }, [location]);

  const handleClose = () => {
    setIsOpen(false);
    localStorage.setItem('audit_popup_dismissed', 'true');
    setDismissed(true);
  };

  const handleCTA = () => {
    setIsOpen(false);
    navigate('/free-audit');
  };

  if (!isOpen || dismissed) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[9999] p-4">
      <div className="bg-background border-2 border-primary rounded-xl shadow-2xl max-w-md w-full p-6 relative animate-in fade-in slide-in-from-bottom-4 duration-300">
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 text-muted-foreground hover:text-foreground"
        >
          <X className="h-5 w-5" />
        </button>

        <div className="text-center mb-6">
          <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <Sparkles className="h-8 w-8 text-primary" />
          </div>
          <h2 className="font-heading text-2xl font-bold mb-2">
            Want to See What You Can Automate?
          </h2>
          <p className="text-muted-foreground">
            Get a free AI-powered automation report for your website in 60 seconds
          </p>
        </div>

        <div className="space-y-4">
          <div className="bg-primary/5 rounded-lg p-4">
            <ul className="space-y-2 text-sm">
              <li className="flex items-center gap-2">
                <span className="text-primary">✓</span>
                <span>Personalized automation recommendations</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-primary">✓</span>
                <span>ROI estimates for each opportunity</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-primary">✓</span>
                <span>100% free, no credit card required</span>
              </li>
            </ul>
          </div>

          <Button onClick={handleCTA} className="w-full" size="lg">
            <Sparkles className="h-5 w-5 mr-2" />
            Generate My Free Report
          </Button>

          <button
            onClick={handleClose}
            className="w-full text-sm text-muted-foreground hover:text-foreground"
          >
            No thanks, maybe later
          </button>
        </div>
      </div>
    </div>
  );
}
