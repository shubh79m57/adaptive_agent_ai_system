'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { agentAPI } from '@/lib/api'
import { Send, Bot, Mail, Phone } from 'lucide-react'

export default function AgentsPage() {
  const [task, setTask] = useState('')
  const [agentType, setAgentType] = useState<'sales' | 'email' | 'auto'>('auto')
  const [result, setResult] = useState<any>(null)

  const executeTaskMutation = useMutation({
    mutationFn: ({ task, agentType }: { task: string; agentType: string }) =>
      agentAPI.executeTask(task, undefined, agentType === 'auto' ? undefined : agentType),
    onSuccess: (data) => {
      setResult(data)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (task.trim()) {
      executeTaskMutation.mutate({ task, agentType })
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">
          Agent Orchestration
        </h1>

        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Agent Type
              </label>
              <div className="flex space-x-4">
                <AgentTypeButton
                  icon={<Bot className="w-5 h-5" />}
                  label="Auto"
                  selected={agentType === 'auto'}
                  onClick={() => setAgentType('auto')}
                />
                <AgentTypeButton
                  icon={<Phone className="w-5 h-5" />}
                  label="Sales"
                  selected={agentType === 'sales'}
                  onClick={() => setAgentType('sales')}
                />
                <AgentTypeButton
                  icon={<Mail className="w-5 h-5" />}
                  label="Email"
                  selected={agentType === 'email'}
                  onClick={() => setAgentType('email')}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Task Description
              </label>
              <textarea
                value={task}
                onChange={(e) => setTask(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={4}
                placeholder="Describe the task you want the agent to perform..."
              />
            </div>

            <button
              type="submit"
              disabled={executeTaskMutation.isPending}
              className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {executeTaskMutation.isPending ? (
                <span>Processing...</span>
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  <span>Execute Task</span>
                </>
              )}
            </button>
          </form>
        </div>

        {result && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-4">Result</h2>
            <div className="bg-gray-50 rounded-lg p-4">
              <pre className="whitespace-pre-wrap text-sm">
                {JSON.stringify(result, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function AgentTypeButton({
  icon,
  label,
  selected,
  onClick,
}: {
  icon: React.ReactNode
  label: string
  selected: boolean
  onClick: () => void
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex items-center space-x-2 px-4 py-2 rounded-lg border-2 transition-colors ${
        selected
          ? 'border-blue-600 bg-blue-50 text-blue-700'
          : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
      }`}
    >
      {icon}
      <span className="font-medium">{label}</span>
    </button>
  )
}
