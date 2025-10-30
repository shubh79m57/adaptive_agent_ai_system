"use client";

import { useState } from 'react';

interface EmailConfig {
  email: string;
  password: string;
}

export default function EmailSendingPage() {
  const [emailConfig, setEmailConfig] = useState<EmailConfig>({
    email: '',
    password: ''
  });
  const [recipient, setRecipient] = useState('');
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [testResult, setTestResult] = useState<any>(null);
  const [sendResult, setSendResult] = useState<any>(null);

  const testEmailConfig = async () => {
    if (!emailConfig.email || !emailConfig.password) {
      alert('Please enter both email and password');
      return;
    }

    setIsLoading(true);
    setTestResult(null);
    
    try {
      const response = await fetch('/api/agents/send-email/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(emailConfig)
      });

      const data = await response.json();
      setTestResult(data);
      
      if (data.success) {
        alert('✅ Email configuration test successful! Check your inbox.');
      } else {
        alert(`❌ Email test failed: ${data.message}`);
      }
    } catch (error) {
      alert('Error testing email configuration');
      setTestResult({ success: false, message: 'Network error' });
    } finally {
      setIsLoading(false);
    }
  };

  const sendEmail = async () => {
    if (!emailConfig.email || !emailConfig.password) {
      alert('Please configure and test your email settings first');
      return;
    }

    if (!recipient || !subject || !body) {
      alert('Please fill in recipient, subject, and body');
      return;
    }

    setIsLoading(true);
    setSendResult(null);
    
    try {
      const response = await fetch('/api/agents/send-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          recipient,
          subject,
          body,
          email_config: emailConfig
        })
      });

      const data = await response.json();
      setSendResult(data);
      
      if (data.success) {
        alert(`✅ Email sent successfully to ${recipient}!`);
        // Clear form
        setRecipient('');
        setSubject('');
        setBody('');
      } else {
        alert(`❌ Failed to send email: ${data.detail || 'Unknown error'}`);
      }
    } catch (error) {
      alert('Error sending email');
      setSendResult({ success: false, message: 'Network error' });
    } finally {
      setIsLoading(false);
    }
  };

  const generateSampleEmail = () => {
    setRecipient('trivitry@gmail.com');
    setSubject('Introduction to Our AI Solutions');
    setBody(`Hi there,

I hope this email finds you well.

I came across your profile and was impressed by your work in the industry.

We've been helping companies like yours achieve:
• 50% reduction in manual processes
• 40% improvement in operational efficiency  
• 25% faster time-to-market

Worth a brief 15-minute conversation to explore how this could apply to your company?

Best regards,
Your Sales Team

P.S. This email was sent automatically by our AI agent system!`);
  };

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          📧 Automatic Email Sending
        </h1>
        <p className="text-gray-600">
          Send emails automatically through your AI agent system
        </p>
      </div>

      {/* Email Configuration */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">⚙️ Email Configuration</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Gmail Address
            </label>
            <input
              type="email"
              value={emailConfig.email}
              onChange={(e) => setEmailConfig({...emailConfig, email: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="your-email@gmail.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Gmail App Password
            </label>
            <input
              type="password"
              value={emailConfig.password}
              onChange={(e) => setEmailConfig({...emailConfig, password: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="16-character app password"
            />
          </div>
        </div>
        
        <button
          onClick={testEmailConfig}
          disabled={isLoading || !emailConfig.email || !emailConfig.password}
          className="px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-gray-400"
        >
          {isLoading ? 'Testing...' : '🧪 Test Email Configuration'}
        </button>

        {testResult && (
          <div className={`mt-4 p-4 rounded-lg ${testResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
            <div className={`font-medium ${testResult.success ? 'text-green-800' : 'text-red-800'}`}>
              {testResult.success ? '✅ Email Configuration Successful!' : '❌ Email Configuration Failed'}
            </div>
            <div className={`text-sm mt-1 ${testResult.success ? 'text-green-600' : 'text-red-600'}`}>
              {testResult.message}
            </div>
          </div>
        )}
      </div>

      {/* Email Composition */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">✉️ Compose Email</h2>
          <button
            onClick={generateSampleEmail}
            className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
          >
            📝 Load Sample Email
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Recipient Email
            </label>
            <input
              type="email"
              value={recipient}
              onChange={(e) => setRecipient(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="recipient@company.com"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Subject Line
            </label>
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Introduction to Our Solutions"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Body
            </label>
            <textarea
              value={body}
              onChange={(e) => setBody(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 h-64"
              placeholder="Write your email content here..."
            />
          </div>
        </div>

        <div className="mt-6">
          <button
            onClick={sendEmail}
            disabled={isLoading || !recipient || !subject || !body || !testResult?.success}
            className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400"
          >
            {isLoading ? 'Sending...' : '🚀 Send Email Now'}
          </button>
          
          {!testResult?.success && (
            <p className="text-sm text-gray-600 mt-2">
              Please test your email configuration first
            </p>
          )}
        </div>

        {sendResult && (
          <div className={`mt-4 p-4 rounded-lg ${sendResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
            <div className={`font-medium ${sendResult.success ? 'text-green-800' : 'text-red-800'}`}>
              {sendResult.success ? '✅ Email Sent Successfully!' : '❌ Email Sending Failed'}
            </div>
            <div className={`text-sm mt-1 ${sendResult.success ? 'text-green-600' : 'text-red-600'}`}>
              {sendResult.message || sendResult.detail || 'Unknown error'}
            </div>
          </div>
        )}
      </div>

      {/* Setup Instructions */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-800 mb-4">📋 Gmail App Password Setup</h3>
        <div className="text-blue-700 space-y-2">
          <p><strong>Step 1:</strong> Go to your Google Account settings</p>
          <p><strong>Step 2:</strong> Navigate to Security → 2-Step Verification</p>
          <p><strong>Step 3:</strong> Scroll down to "App passwords"</p>
          <p><strong>Step 4:</strong> Generate a new app password for "Mail"</p>
          <p><strong>Step 5:</strong> Copy the 16-character password and paste it above</p>
          <p><strong>Step 6:</strong> Test the configuration before sending emails</p>
        </div>
        
        <div className="mt-4 p-4 bg-yellow-100 border border-yellow-200 rounded">
          <p className="text-yellow-800 text-sm">
            <strong>Security Note:</strong> App passwords are safer than using your regular Gmail password. 
            They can be revoked anytime from your Google Account settings.
          </p>
        </div>
      </div>

      {/* Integration with AI Agent */}
      <div className="bg-gray-50 rounded-lg p-6 mt-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">🤖 AI Agent Integration</h3>
        <div className="text-gray-700 space-y-2">
          <p>Once your email is configured, you can use the AI agent to send emails automatically:</p>
          <ul className="list-disc list-inside space-y-1 ml-4">
            <li>Say: <em>"Actually send email to john@company.com about our product"</em></li>
            <li>Say: <em>"Send bulk emails to our prospect list"</em></li>
            <li>Say: <em>"Auto-send that email we generated"</em></li>
          </ul>
          <p className="mt-4">
            <strong>Go back to:</strong> <a href="/" className="text-blue-600 hover:underline">Main Agent Interface</a> to test automatic sending!
          </p>
        </div>
      </div>
    </div>
  );
}