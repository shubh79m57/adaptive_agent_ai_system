# Adaptive AI Agent System

A production-ready multi-agent AI system with real-time voice capabilities, adaptive learning, and comprehensive GTM (Go-To-Market) orchestration built with LangChain, LangGraph, LiveKit, and modern web technologies.

## 🚀 Features

- **Multi-Agent Orchestration**: LangGraph-powered agent coordination for complex workflows
- **Real-time Voice**: LiveKit integration for live sales calls with AI agents
- **Adaptive Learning**: Continuous learning from every interaction
- **Custom RAG Pipelines**: Retrieval-augmented generation with proprietary GTM data
- **Vector Search**: pgvector & Pinecone for semantic search
- **Analytics**: ClickHouse-powered performance tracking
- **Workflow Orchestration**: Temporal for durable workflows
- **Modern UI**: Next.js 14 with TypeScript and Tailwind CSS

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **FastAPI**: High-performance async API
- **LangChain & LangGraph**: Agent orchestration and workflows
- **LiveKit**: Real-time voice communication
- **Temporal**: Durable workflow execution
- **PostgreSQL + pgvector**: Vector storage
- **ClickHouse**: Analytics database
- **Redis**: Caching and memory
- **Pinecone**: Cloud vector database

### Frontend (Next.js/TypeScript)
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **TailwindCSS**: Utility-first styling
- **React Query**: Data fetching and caching
- **LiveKit Components**: Voice UI components

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ with pgvector extension
- Redis 7+
- ClickHouse 23+
- Temporal Server (optional, for workflows)
- LiveKit Server (for voice features)

## 🛠️ Installation

### 1. Clone and Setup

```bash
cd adaptive-ai-agent-system
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Edit .env with your API keys and configuration
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb adaptive_ai_db

# Install pgvector extension
psql adaptive_ai_db -c "CREATE EXTENSION vector;"

# Run migrations (if using Alembic)
alembic upgrade head
```

### 4. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
echo "NEXT_PUBLIC_LIVEKIT_URL=wss://your-livekit-server.com" >> .env.local
```

## 🚀 Running the Application

### Start Backend

```bash
cd backend
python -m app.main
# Server runs on http://localhost:8000
```

### Start Frontend

```bash
cd frontend
npm run dev
# UI runs on http://localhost:3000
```

### Start Temporal Worker (Optional)

```bash
cd workflows
python worker.py
```

## 📁 Project Structure

```
adaptive-ai-agent-system/
├── backend/
│   ├── app/
│   │   ├── agents/          # Agent implementations
│   │   │   ├── adaptive_agent.py
│   │   │   └── multi_agent_orchestrator.py
│   │   ├── api/             # API routes
│   │   │   ├── agents.py
│   │   │   ├── voice.py
│   │   │   ├── analytics.py
│   │   │   └── workflows.py
│   │   ├── core/            # Core configuration
│   │   │   └── config.py
│   │   ├── models/          # Data models
│   │   ├── rag/             # RAG implementation
│   │   │   └── retriever.py
│   │   ├── services/        # Business logic
│   │   │   ├── memory_service.py
│   │   │   └── analytics_service.py
│   │   ├── voice/           # LiveKit integration
│   │   │   └── livekit_agent.py
│   │   └── main.py          # Application entry point
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── agents/          # Agent UI
│   │   ├── voice/           # Voice call UI
│   │   ├── email/           # Email campaign UI
│   │   ├── analytics/       # Analytics dashboard
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── providers.tsx
│   ├── components/          # Reusable components
│   ├── lib/                 # Utilities and API clients
│   │   └── api.ts
│   ├── package.json
│   └── tsconfig.json
├── workflows/               # Temporal workflows
│   ├── temporal_workflows.py
│   └── worker.py
└── README.md
```

## 🔑 Configuration

### Environment Variables

#### Backend (.env)

```env
# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
PINECONE_API_KEY=...
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...

# Databases
POSTGRES_HOST=localhost
POSTGRES_DB=adaptive_ai_db
CLICKHOUSE_HOST=localhost
REDIS_HOST=localhost

# Optional
LANGCHAIN_API_KEY=...  # For LangSmith tracing
```

#### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_LIVEKIT_URL=wss://your-livekit-server.com
```

## 🤖 Agent Types

### 1. Sales Agent
- Handles sales conversations
- Customer profile retrieval
- Next action suggestions
- Real-time voice integration

### 2. Outbound Email Agent
- Generates personalized emails
- Campaign management
- Response tracking
- Adaptive learning from responses

### 3. Multi-Agent Orchestrator
- Coordinates multiple agents
- LangGraph-based routing
- Context sharing
- Result synthesis

## 📊 API Endpoints

### Agents
- `POST /api/agents/execute` - Execute agent task
- `POST /api/agents/generate-email` - Generate outbound email
- `GET /api/agents/status` - Get agent status

### Voice
- `POST /api/voice/room/create` - Create voice room
- `POST /api/voice/token/generate` - Generate access token
- `POST /api/voice/conversation/process` - Process conversation
- `POST /api/voice/recording/start/{room_name}` - Start recording
- `POST /api/voice/recording/stop/{room_name}` - Stop recording

### Analytics
- `GET /api/analytics/performance/{agent_type}` - Agent performance
- `GET /api/analytics/voice-calls` - Voice call metrics
- `GET /api/analytics/dashboard` - Dashboard metrics

### Workflows
- `POST /api/workflows/execute` - Execute Temporal workflow
- `GET /api/workflows/status/{workflow_id}` - Workflow status

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test
```

## 📈 Monitoring & Observability

- **LangSmith**: Agent tracing and debugging
- **ClickHouse**: Performance analytics
- **Redis**: Memory and caching metrics
- **Temporal**: Workflow execution tracking

## 🔒 Security

- API key management via environment variables
- CORS configuration
- Rate limiting (implement as needed)
- Data encryption at rest and in transit

## 🚢 Deployment

### Docker Deployment (Recommended)

```bash
# Build containers
docker-compose build

# Start services
docker-compose up -d
```

### Manual Deployment

1. Deploy backend to cloud platform (AWS, GCP, Azure)
2. Deploy frontend to Vercel/Netlify
3. Setup databases (managed services recommended)
4. Configure environment variables
5. Setup monitoring and logging

## 📚 Key Technologies

- **LangChain**: Agent framework
- **LangGraph**: Multi-agent orchestration
- **LiveKit**: Real-time voice
- **FastAPI**: Backend API
- **Next.js**: Frontend framework
- **Temporal**: Workflow engine
- **ClickHouse**: Analytics database
- **PostgreSQL + pgvector**: Vector storage
- **Pinecone**: Cloud vector database
- **Redis**: Caching and queues

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:
- GitHub Issues
- Documentation
- Community Discord

## 🎯 Roadmap

- [ ] Fine-tuning pipeline for custom models
- [ ] Multi-language support
- [ ] Advanced sentiment analysis
- [ ] Integration with CRM systems
- [ ] Mobile app (React Native)
- [ ] Real-time collaboration features
- [ ] A/B testing framework
- [ ] Advanced reporting dashboard

## 🏆 Best Practices

1. **Agent Design**: Keep agents focused and specialized
2. **Memory Management**: Use Redis for short-term, vector DB for long-term
3. **Monitoring**: Enable LangSmith tracing in development
4. **Testing**: Write tests for critical agent workflows
5. **Security**: Never commit API keys, use environment variables
6. **Scaling**: Use Temporal for long-running workflows
7. **Performance**: Monitor ClickHouse query performance

---

Built with ❤️ for modern GTM teams
