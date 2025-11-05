import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'sonner';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import FreeAuditPopup from './components/FreeAuditPopup';
import Landing from './pages/Landing';
import Login from './pages/Login';
import FreeAudit from './pages/FreeAudit';
import Reports from './pages/Reports';
import ContentGenerator from './pages/ContentGenerator';
import EmailAssistant from './pages/EmailAssistant';
import WorkflowBuilder from './pages/WorkflowBuilder';
import Marketplace from './pages/Marketplace';
import TeamSettings from './pages/TeamSettings';
import Settings from './pages/Settings';
import WorkforceScan from './pages/WorkforceScan';
import Dashboard from './pages/Dashboard';
import SetupWizard from './pages/SetupWizard';
import Billing from './pages/Billing';
import BillingSuccess from './pages/BillingSuccess';
import ChatbotSetup from './pages/ChatbotSetup';
import LeadCapture from './pages/LeadCapture';
import Analytics from './pages/Analytics';
import './App.css';

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="min-h-screen bg-background">
          <Toaster position="top-right" />
          <FreeAuditPopup />
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/free-audit" element={<FreeAudit />} />
            <Route path="/login" element={<Login />} />
            <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/reports" element={<ProtectedRoute><Reports /></ProtectedRoute>} />
            <Route path="/content-generator" element={<ProtectedRoute><ContentGenerator /></ProtectedRoute>} />
            <Route path="/email-assistant" element={<ProtectedRoute><EmailAssistant /></ProtectedRoute>} />
            <Route path="/workflow-builder" element={<ProtectedRoute><WorkflowBuilder /></ProtectedRoute>} />
            <Route path="/marketplace" element={<ProtectedRoute><Marketplace /></ProtectedRoute>} />
            <Route path="/team" element={<ProtectedRoute><TeamSettings /></ProtectedRoute>} />
            <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
            <Route path="/setup/:automationId" element={<ProtectedRoute><SetupWizard /></ProtectedRoute>} />
            <Route path="/billing" element={<ProtectedRoute><Billing /></ProtectedRoute>} />
            <Route path="/billing/success" element={<ProtectedRoute><BillingSuccess /></ProtectedRoute>} />
            <Route path="/chatbot/:automationId" element={<ProtectedRoute><ChatbotSetup /></ProtectedRoute>} />
            <Route path="/leads" element={<ProtectedRoute><LeadCapture /></ProtectedRoute>} />
            <Route path="/analytics" element={<ProtectedRoute><Analytics /></ProtectedRoute>} />
          </Routes>
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;
