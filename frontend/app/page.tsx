import Link from 'next/link'
import { Activity, Mail, Phone, BarChart3 } from 'lucide-react'

export default function Home() {
  return (
    <main className="min-h-screen p-8 bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto">
        <header className="mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Adaptive AI Agent System
          </h1>
          <p className="text-xl text-gray-600">
            Multi-agent AI backbone for modern go-to-market teams
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <DashboardCard
            title="Agent Orchestration"
            description="Multi-agent coordination with LangGraph"
            icon={<Activity className="w-8 h-8 text-blue-600" />}
            href="/agents"
          />
          <DashboardCard
            title="Voice Calls"
            description="Real-time voice with LiveKit"
            icon={<Phone className="w-8 h-8 text-green-600" />}
            href="/voice"
          />
          <DashboardCard
            title="Email Campaigns"
            description="Adaptive outbound emails"
            icon={<Mail className="w-8 h-8 text-purple-600" />}
            href="/email"
          />
          <DashboardCard
            title="Analytics"
            description="Performance tracking & insights"
            icon={<BarChart3 className="w-8 h-8 text-orange-600" />}
            href="/analytics"
          />
        </div>

        <section className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-3xl font-bold mb-6">Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <FeatureItem
              title="Adaptive Learning"
              description="Agents continuously learn from every interaction"
            />
            <FeatureItem
              title="Real-time Voice"
              description="LiveKit integration for live sales calls"
            />
            <FeatureItem
              title="Multi-Agent Coordination"
              description="LangGraph-powered agent orchestration"
            />
            <FeatureItem
              title="Custom RAG Pipelines"
              description="Retrieval-augmented generation with GTM data"
            />
            <FeatureItem
              title="Vector Search"
              description="pgvector & Pinecone for semantic search"
            />
            <FeatureItem
              title="Analytics Dashboard"
              description="ClickHouse-powered insights"
            />
          </div>
        </section>
      </div>
    </main>
  )
}

function DashboardCard({ title, description, icon, href }: {
  title: string
  description: string
  icon: React.ReactNode
  href: string
}) {
  return (
    <Link href={href}>
      <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow cursor-pointer">
        <div className="mb-4">{icon}</div>
        <h3 className="text-xl font-semibold mb-2">{title}</h3>
        <p className="text-gray-600">{description}</p>
      </div>
    </Link>
  )
}

function FeatureItem({ title, description }: {
  title: string
  description: string
}) {
  return (
    <div className="flex items-start space-x-3">
      <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center mt-1">
        <div className="w-2 h-2 rounded-full bg-blue-600"></div>
      </div>
      <div>
        <h4 className="font-semibold text-gray-900">{title}</h4>
        <p className="text-gray-600 text-sm">{description}</p>
      </div>
    </div>
  )
}
