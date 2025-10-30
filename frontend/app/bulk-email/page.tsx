"use client";

import { useState } from 'react';

interface Prospect {
  email: string;
  name: string;
  company: string;
  role: string;
  context?: string;
}

interface EmailConfig {
  email: string;
  password: string;
  smtp_server?: string;
  imap_server?: string;
}

interface CampaignStats {
  total_sent: number;
  total_replies: number;
  response_rate: number;
  interest_rate: number;
}

export default function BulkEmailPage() {
  const [prospects, setProspects] = useState<Prospect[]>([]);
  const [emailConfig, setEmailConfig] = useState<EmailConfig>({
    email: '',
    password: '',
    smtp_server: 'smtp.gmail.com',
    imap_server: 'imap.gmail.com'
  });
  const [campaignName, setCampaignName] = useState('');
  const [delaySeconds, setDelaySeconds] = useState(60);
  const [isLoading, setIsLoading] = useState(false);
  const [previews, setPreviews] = useState([]);
  const [campaignStats, setCampaignStats] = useState<CampaignStats | null>(null);

  const addProspect = () => {
    setProspects([...prospects, {
      email: '',
      name: '',
      company: '',
      role: '',
      context: 'general outreach'
    }]);
  };

  const updateProspect = (index: number, field: keyof Prospect, value: string) => {
    const updated = [...prospects];
    updated[index] = { ...updated[index], [field]: value };
    setProspects(updated);
  };

  const removeProspect = (index: number) => {
    setProspects(prospects.filter((_, i) => i !== index));
  };

  const previewCampaign = async () => {
    if (prospects.length === 0) {
      alert('Please add at least one prospect');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch('/api/agents/bulk-email/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prospects,
          campaign_type: 'outreach',
          delay_seconds: delaySeconds
        })
      });

      const data = await response.json();
      if (data.success) {
        setPreviews(data.email_previews);
      } else {
        alert('Error previewing campaign');
      }
    } catch (error) {
      alert('Error previewing campaign');
    } finally {
      setIsLoading(false);
    }
  };

  const sendCampaign = async () => {
    if (!emailConfig.email || !emailConfig.password) {
      alert('Please configure your email settings');
      return;
    }

    if (prospects.length === 0) {
      alert('Please add at least one prospect');
      return;
    }

    setIsLoading(true);
    try {
      // First, save prospects to CSV (simulated)
      const csvContent = "email,name,company,role,context\n" + 
        prospects.map(p => `${p.email},${p.name},${p.company},${p.role},${p.context || 'general outreach'}`).join('\n');
      
      const response = await fetch('/api/agents/bulk-email/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email_config: emailConfig,
          campaign_name: campaignName,
          send_delay: delaySeconds,
          csv_file_path: 'prospects.csv'
        })
      });

      const data = await response.json();
      if (data.success) {
        alert(`Campaign "${campaignName}" started successfully!`);
        setCampaignStats(data);
      } else {
        alert(`Error: ${data.message}`);
      }
    } catch (error) {
      alert('Error sending campaign');
    } finally {
      setIsLoading(false);
    }
  };

  const monitorResponses = async () => {
    if (!emailConfig.email || !emailConfig.password) {
      alert('Please configure your email settings');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch('/api/agents/bulk-email/monitor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(emailConfig)
      });

      const data = await response.json();
      if (data.success) {
        setCampaignStats(data.campaign_stats);
        alert('Email responses monitored and processed!');
      } else {
        alert(`Error: ${data.message}`);
      }
    } catch (error) {
      alert('Error monitoring responses');
    } finally {
      setIsLoading(false);
    }
  };

  const loadSampleData = () => {
    setProspects([
      {
        email: 'john@techcorp.com',
        name: 'John Smith',
        company: 'TechCorp Inc',
        role: 'CEO',
        context: 'general outreach'
      },
      {
        email: 'jane@startup.com',
        name: 'Jane Doe',
        company: 'StartupXYZ',
        role: 'VP Sales',
        context: 'product demo'
      },
      {
        email: 'mike@enterprise.com',
        name: 'Mike Johnson',
        company: 'Enterprise Solutions',
        role: 'CTO',
        context: 'technical discussion'
      }
    ]);
  };

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          🚀 Bulk Email Campaign Manager
        </h1>
        <p className="text-gray-600">
          Send personalized email campaigns with automated response handling
        </p>
      </div>

      {/* Email Configuration */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">📧 Email Configuration</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Address
            </label>
            <input
              type="email"
              value={emailConfig.email}
              onChange={(e) => setEmailConfig({...emailConfig, email: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="your-sales@company.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              App Password
            </label>
            <input
              type="password"
              value={emailConfig.password}
              onChange={(e) => setEmailConfig({...emailConfig, password: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="App password (not regular password)"
            />
          </div>
        </div>
      </div>

      {/* Campaign Settings */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">⚙️ Campaign Settings</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Campaign Name
            </label>
            <input
              type="text"
              value={campaignName}
              onChange={(e) => setCampaignName(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Q4 Outreach Campaign"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Delay Between Emails (seconds)
            </label>
            <input
              type="number"
              value={delaySeconds}
              onChange={(e) => setDelaySeconds(Number(e.target.value))}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              min="30"
              max="300"
            />
          </div>
        </div>
      </div>

      {/* Prospect Management */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">👥 Prospect List ({prospects.length})</h2>
          <div className="space-x-2">
            <button
              onClick={loadSampleData}
              className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
            >
              Load Sample Data
            </button>
            <button
              onClick={addProspect}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
              + Add Prospect
            </button>
          </div>
        </div>

        {prospects.map((prospect, index) => (
          <div key={index} className="border border-gray-200 rounded-lg p-4 mb-4">
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div>
                <label className="block text-sm text-gray-600 mb-1">Email</label>
                <input
                  type="email"
                  value={prospect.email}
                  onChange={(e) => updateProspect(index, 'email', e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                  placeholder="email@company.com"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Name</label>
                <input
                  type="text"
                  value={prospect.name}
                  onChange={(e) => updateProspect(index, 'name', e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                  placeholder="John Smith"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Company</label>
                <input
                  type="text"
                  value={prospect.company}
                  onChange={(e) => updateProspect(index, 'company', e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                  placeholder="TechCorp Inc"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Role</label>
                <select
                  value={prospect.role}
                  onChange={(e) => updateProspect(index, 'role', e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Role</option>
                  <option value="CEO">CEO</option>
                  <option value="CTO">CTO</option>
                  <option value="VP Sales">VP Sales</option>
                  <option value="VP Marketing">VP Marketing</option>
                  <option value="Director">Director</option>
                  <option value="Manager">Manager</option>
                </select>
              </div>
              <div className="flex items-end">
                <button
                  onClick={() => removeProspect(index)}
                  className="w-full p-2 bg-red-500 text-white rounded hover:bg-red-600"
                >
                  Remove
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Action Buttons */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex flex-wrap gap-4">
          <button
            onClick={previewCampaign}
            disabled={isLoading || prospects.length === 0}
            className="px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-gray-400"
          >
            {isLoading ? 'Loading...' : '👀 Preview Campaign'}
          </button>
          
          <button
            onClick={sendCampaign}
            disabled={isLoading || prospects.length === 0 || !emailConfig.email}
            className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400"
          >
            {isLoading ? 'Sending...' : '🚀 Send Campaign'}
          </button>
          
          <button
            onClick={monitorResponses}
            disabled={isLoading || !emailConfig.email}
            className="px-6 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:bg-gray-400"
          >
            {isLoading ? 'Monitoring...' : '📊 Monitor Responses'}
          </button>
        </div>
      </div>

      {/* Email Previews */}
      {previews.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">👀 Email Previews</h2>
          {previews.map((preview: any, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4 mb-4">
              <div className="mb-2">
                <strong>To:</strong> {preview.prospect.name} ({preview.prospect.email})
              </div>
              <div className="mb-2">
                <strong>Subject:</strong> {preview.subject}
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <pre className="whitespace-pre-wrap text-sm">{preview.body}</pre>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Campaign Stats */}
      {campaignStats && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">📈 Campaign Statistics</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{campaignStats.total_sent}</div>
              <div className="text-sm text-gray-600">Emails Sent</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{campaignStats.total_replies}</div>
              <div className="text-sm text-gray-600">Replies Received</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{campaignStats.response_rate?.toFixed(1)}%</div>
              <div className="text-sm text-gray-600">Response Rate</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{campaignStats.interest_rate?.toFixed(1)}%</div>
              <div className="text-sm text-gray-600">Interest Rate</div>
            </div>
          </div>
        </div>
      )}

      {/* Help Section */}
      <div className="bg-blue-50 rounded-lg p-6 mt-6">
        <h3 className="text-lg font-semibold text-blue-800 mb-2">💡 How It Works</h3>
        <ul className="text-blue-700 space-y-1">
          <li>• <strong>Setup:</strong> Configure your email settings (use app passwords for Gmail)</li>
          <li>• <strong>Add Prospects:</strong> Add prospects manually or load sample data</li>
          <li>• <strong>Preview:</strong> See how emails will look before sending</li>
          <li>• <strong>Send:</strong> Launch your personalized email campaign</li>
          <li>• <strong>Monitor:</strong> AI automatically processes responses and categorizes them</li>
          <li>• <strong>Follow-up:</strong> AI generates appropriate follow-up emails based on responses</li>
        </ul>
      </div>
    </div>
  );
}