'use client'

import { useQuery } from '@tanstack/react-query'
import { analyticsAPI } from '@/lib/api'
import { BarChart3, TrendingUp, Phone, Mail } from 'lucide-react'

export default function AnalyticsPage() {
  const { data: dashboardData, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => analyticsAPI.getDashboardMetrics(),
    refetchInterval: 30000,
  })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 to-yellow-100 p-8 flex items-center justify-center">
        <div className="text-2xl font-bold">Loading analytics...</div>
      </div>
    )
  }

  const dashboard = dashboardData?.dashboard || {}

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-yellow-100 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">
          Analytics Dashboard
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <MetricCard
            title="Sales Agent"
            icon={<Phone className="w-8 h-8 text-blue-600" />}
            metrics={dashboard.sales_agent || {}}
          />
          <MetricCard
            title="Email Agent"
            icon={<Mail className="w-8 h-8 text-purple-600" />}
            metrics={dashboard.email_agent || {}}
          />
          <MetricCard
            title="Voice Calls"
            icon={<BarChart3 className="w-8 h-8 text-green-600" />}
            metrics={dashboard.voice_calls || {}}
          />
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold mb-6 flex items-center space-x-2">
            <TrendingUp className="w-6 h-6 text-orange-600" />
            <span>Performance Overview</span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <PerformanceSection
              title="Sales Agent Performance"
              data={dashboard.sales_agent}
            />
            <PerformanceSection
              title="Email Agent Performance"
              data={dashboard.email_agent}
            />
          </div>

          <div className="mt-6">
            <h3 className="text-xl font-bold mb-4">Voice Call Analytics</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatBox
                label="Total Calls"
                value={dashboard.voice_calls?.total_calls || 0}
              />
              <StatBox
                label="Avg Duration"
                value={`${Math.round(dashboard.voice_calls?.avg_duration_seconds || 0)}s`}
              />
              <StatBox
                label="Avg Sentiment"
                value={(dashboard.voice_calls?.avg_sentiment || 0).toFixed(2)}
              />
              <StatBox
                label="Success Rate"
                value={`${Math.round((dashboard.voice_calls?.success_rate || 0) * 100)}%`}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function MetricCard({ title, icon, metrics }: any) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold">{title}</h3>
        {icon}
      </div>
      <div className="space-y-2">
        <div className="flex justify-between">
          <span className="text-gray-600">Interactions:</span>
          <span className="font-bold">{metrics.total_interactions || 0}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">Success Rate:</span>
          <span className="font-bold text-green-600">
            {Math.round((metrics.success_rate || 0) * 100)}%
          </span>
        </div>
      </div>
    </div>
  )
}

function PerformanceSection({ title, data }: any) {
  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <h4 className="font-bold mb-3">{title}</h4>
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span>Total Interactions:</span>
          <span className="font-semibold">{data?.total_interactions || 0}</span>
        </div>
        <div className="flex justify-between">
          <span>Successful:</span>
          <span className="font-semibold text-green-600">
            {data?.successful_interactions || 0}
          </span>
        </div>
        <div className="flex justify-between">
          <span>Avg Duration:</span>
          <span className="font-semibold">
            {Math.round(data?.avg_duration_ms || 0)}ms
          </span>
        </div>
        <div className="flex justify-between">
          <span>Success Rate:</span>
          <span className="font-semibold">
            {Math.round((data?.success_rate || 0) * 100)}%
          </span>
        </div>
      </div>
    </div>
  )
}

function StatBox({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <div className="text-sm text-gray-600 mb-1">{label}</div>
      <div className="text-2xl font-bold">{value}</div>
    </div>
  )
}
