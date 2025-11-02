import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CheckCircle, Loader } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function BillingSuccess() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState('checking');
  const [attempts, setAttempts] = useState(0);

  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    if (!sessionId) {
      navigate('/billing');
      return;
    }

    pollPaymentStatus(sessionId);
  }, []);

  const pollPaymentStatus = async (sessionId, attemptNum = 0) => {
    if (attemptNum >= 5) {
      setStatus('timeout');
      return;
    }

    try {
      const response = await fetch(`${BACKEND_URL}/api/billing/status/${sessionId}`, {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        
        if (data.status === 'completed') {
          setStatus('success');
          toast.success('Payment successful! Your plan has been upgraded.');
          return;
        } else if (data.status === 'failed') {
          setStatus('failed');
          return;
        }

        // Still pending, poll again
        setAttempts(attemptNum + 1);
        setTimeout(() => pollPaymentStatus(sessionId, attemptNum + 1), 2000);
      }
    } catch (error) {
      console.error('Payment status error:', error);
      setStatus('error');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/30 p-4">
      <Card className="max-w-md w-full">
        <CardHeader>
          <CardTitle className="text-center">
            {status === 'checking' && 'Processing Payment...'}
            {status === 'success' && 'Payment Successful!'}
            {status === 'failed' && 'Payment Failed'}
            {status === 'timeout' && 'Payment Processing'}
            {status === 'error' && 'Something Went Wrong'}
          </CardTitle>
        </CardHeader>
        <CardContent className="text-center space-y-6">
          {status === 'checking' && (
            <>
              <Loader className="h-16 w-16 animate-spin text-primary mx-auto" />
              <p className="text-muted-foreground">
                Verifying your payment... (Attempt {attempts + 1}/5)
              </p>
            </>
          )}

          {status === 'success' && (
            <>
              <CheckCircle className="h-16 w-16 text-success mx-auto" />
              <p className="text-muted-foreground">
                Your subscription has been activated. You now have access to premium features!
              </p>
              <Button onClick={() => navigate('/dashboard')} className="w-full">
                Go to Dashboard
              </Button>
            </>
          )}

          {status === 'failed' && (
            <>
              <div className="text-4xl">❌</div>
              <p className="text-muted-foreground">
                Payment was not successful. Please try again or contact support.
              </p>
              <Button onClick={() => navigate('/billing')} className="w-full">
                Back to Billing
              </Button>
            </>
          )}

          {status === 'timeout' && (
            <>
              <div className="text-4xl">⏰</div>
              <p className="text-muted-foreground">
                Payment is still processing. Check your email for confirmation, or refresh this page.
              </p>
              <div className="flex gap-2">
                <Button onClick={() => window.location.reload()} className="flex-1">
                  Refresh
                </Button>
                <Button onClick={() => navigate('/billing')} variant="outline" className="flex-1">
                  Back to Billing
                </Button>
              </div>
            </>
          )}

          {status === 'error' && (
            <>
              <div className="text-4xl">⚠️</div>
              <p className="text-muted-foreground">
                We encountered an error checking your payment. Please contact support if payment was deducted.
              </p>
              <Button onClick={() => navigate('/billing')} className="w-full">
                Back to Billing
              </Button>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
