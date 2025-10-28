'use client'

import { useState } from 'react'
import { useMutation } from '@tantml:invoke>
<parameter name="agentAPI } from '@/lib/api'
import { Mail, Send } from 'lucide-react'

export default function EmailPage() {
  const [prospectName, setProspectName] = useState('')
  const [prospectCompany, setProspectCompany] = useState('')
  const [prospectRole, setProspectRole] = useState('')
  const [context, setContext] = useState('')
  const [generatedEmail, setGeneratedEmail] = useState<string | null>(null)

  const generateEmailMutation = useMutation({
    mutationFn: () =>
      agentAPI.generateEmail({
        prospect_name: prospectName,
        prospect_company: prospectCompany,
        prospect_role: prospectRole,
        context,
      }),
    onSuccess: (data) => {
      setGeneratedEmail(data.email)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (prospectName && prospectCompany && prospectRole) {
      generateEmailMutation.mutate()
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">
          Email Campaign Generator
        </h1>

        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-2xl font-bold mb-4 flex items-center space-x-2">
            <Mail className="w-6 h-6 text-purple-600" />
            <span>Generate Outbound Email</span>
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Prospect Name
                </label>
                <input
                  type="text"
                  value={prospectName}
                  onChange={(e) => setProspectName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  placeholder="John Doe"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Company
                </label>
                <input
                  type="text"
                  value={prospectCompany}
                  onChange={(e) => setProspectCompany(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  placeholder="Acme Corp"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Role
              </label>
              <input
                type="text"
                value={prospectRole}
                onChange={(e) => setProspectRole(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                placeholder="VP of Sales"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Additional Context (Optional)
              </label>
              <textarea
                value={context}
                onChange={(e) => setContext(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                rows={3}
                placeholder="Any additional context about the prospect or campaign..."
              />
            </div>

            <button
              type="submit"
              disabled={generateEmailMutation.isPending}
              className="w-full bg-purple-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {generateEmailMutation.isPending ? (
                <span>Generating...</span>
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  <span>Generate Email</span>
                </>
              )}
            </button>
          </form>
        </div>

        {generatedEmail && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-4">Generated Email</h2>
            <div className="bg-gray-50 rounded-lg p-6">
              <div className="prose max-w-none">
                <pre className="whitespace-pre-wrap font-sans text-sm">
                  {generatedEmail}
                </pre>
              </div>
            </div>

            <div className="mt-4 flex space-x-4">
              <button
                onClick={() => navigator.clipboard.writeText(generatedEmail)}
                className="bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700"
              >
                Copy to Clipboard
              </button>
              <button
                onClick={() => setGeneratedEmail(null)}
                className="bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700"
              >
                Clear
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
