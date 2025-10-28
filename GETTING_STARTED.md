# 🚀 GETTING STARTED

Welcome to the Adaptive AI Agent System! This guide will get you up and running quickly.

## 📋 What You Need

### Required:
- **OpenAI API Key**: https://platform.openai.com/api-keys
- **Python 3.11+**: https://www.python.org/downloads/
- **Node.js 18+**: https://nodejs.org/

### Optional (for full features):
- **Anthropic API Key**: https://console.anthropic.com/
- **Pinecone API Key**: https://www.pinecone.io/
- **LiveKit Account**: https://livekit.io/
- **Docker**: https://www.docker.com/ (for easy deployment)

## ⚡ 3-Minute Quick Start

### Option 1: Docker (Recommended - Easiest)

```bash
# 1. Navigate to project
cd adaptive-ai-agent-system

# 2. Setup environment
cp backend/.env.example backend/.env

# 3. Edit backend/.env and add:
#    OPENAI_API_KEY=sk-your-key-here
#    ANTHROPIC_API_KEY=sk-ant-your-key-here
#    (Use any text editor)

# 4. Start everything!
docker-compose up -d

# 5. Open browser
#    Frontend: http://localhost:3000
#    API Docs: http://localhost:8000/docs
```

### Option 2: Manual (More Control)

**Terminal 1 - Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your API keys
python -m app.main
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```

## 🎯 First Actions

### 1. Test Agent Execution (Web UI)
1. Go to http://localhost:3000
2. Click "Agent Orchestration"
3. Type: "Draft a professional email introducing our AI platform"
4. Click "Execute Task"
5. See AI-generated result!

### 2. Generate Outbound Email
1. Click "Email Campaign Generator"
2. Fill in:
   - Name: "Sarah Johnson"
   - Company: "TechCorp"
   - Role: "VP of Sales"
3. Click "Generate Email"
4. Get personalized email!

### 3. Test API Directly

```bash
# Check health
curl http://localhost:8000/health

# Execute agent task
curl -X POST http://localhost:8000/api/agents/execute \
  -H "Content-Type: application/json" \
  -d '{"task": "Analyze customer feedback", "agent_type": "sales"}'
```

## 📚 Project Structure Overview

```
adaptive-ai-agent-system/
├── backend/               ← Python API & Agents
│   ├── app/
│   │   ├── agents/       ← Agent logic (START HERE)
│   │   ├── api/          ← API endpoints
│   │   ├── rag/          ← Vector search & RAG
│   │   └── voice/        ← LiveKit integration
│   └── examples/         ← Usage examples
├── frontend/             ← Next.js UI
│   ├── app/
│   │   ├── agents/       ← Agent control UI
│   │   ├── voice/        ← Voice call UI
│   │   ├── email/        ← Email generator UI
│   │   └── analytics/    ← Dashboard
│   └── lib/api.ts        ← API client
└── workflows/            ← Temporal workflows
```

## 🔍 Key Files to Explore

### Backend:
1. **`backend/app/agents/adaptive_agent.py`** - Core agent implementation
2. **`backend/app/agents/multi_agent_orchestrator.py`** - Multi-agent coordination
3. **`backend/app/rag/retriever.py`** - RAG & vector search
4. **`backend/app/voice/livekit_agent.py`** - Voice integration
5. **`backend/app/main.py`** - API entry point

### Frontend:
1. **`frontend/app/page.tsx`** - Home page
2. **`frontend/app/agents/page.tsx`** - Agent UI
3. **`frontend/lib/api.ts`** - API client

### Examples:
1. **`backend/examples/sales_agent_example.py`** - Sales agent usage
2. **`backend/examples/multi_agent_example.py`** - Multi-agent orchestration
3. **`backend/examples/rag_example.py`** - RAG system usage

## 🛠️ Development Workflow

### Making Changes:

**Backend Changes:**
```bash
cd backend
# Edit files in app/
# Server auto-reloads with changes
```

**Frontend Changes:**
```bash
cd frontend
# Edit files in app/ or components/
# Browser auto-refreshes with changes
```

### Running Examples:
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python examples/sales_agent_example.py
python examples/multi_agent_example.py
```

## 🔧 Configuration

### Minimum Configuration (backend/.env):
```env
OPENAI_API_KEY=sk-your-key
SECRET_KEY=any-random-string
POSTGRES_DB=adaptive_ai_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

### Full Configuration:
See `backend/.env.example` for all options.

## 🌐 Available Endpoints

Once running, visit:
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs (Interactive!)
- **Health Check**: http://localhost:8000/health

## 🎓 Learning Path

### Day 1: Get Familiar
1. ✅ Run the application
2. ✅ Test agent execution via UI
3. ✅ Generate an email
4. ✅ Explore API docs

### Day 2: Understand Code
1. 📖 Read `adaptive_agent.py`
2. 📖 Run examples
3. 📖 Review multi-agent orchestration
4. 📖 Check RAG implementation

### Day 3: Customize
1. ⚙️ Modify agent prompts
2. ⚙️ Add custom tools
3. ⚙️ Customize UI
4. ⚙️ Test changes

### Day 4+: Advanced
1. 🚀 Add new agent types
2. 🚀 Integrate with CRM
3. 🚀 Fine-tune models
4. 🚀 Deploy to production

## 🆘 Troubleshooting

### "Module not found" errors
```bash
# Make sure virtual environment is activated
cd backend
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### "Connection refused" errors
```bash
# Make sure services are running
# Docker: docker-compose ps
# Manual: Check if PostgreSQL, Redis are running
```

### Port already in use
```bash
# Change ports in docker-compose.yml or .env files
# Or stop the conflicting service
```

### API key errors
```bash
# Double-check .env file has correct keys
# No spaces around = sign
# Keys should start with sk- or sk-ant-
```

## 💡 Tips & Tricks

1. **Use API Docs**: http://localhost:8000/docs for interactive testing
2. **Check Logs**: Backend terminal shows detailed logs
3. **Read Examples**: Start with examples/ directory
4. **Iterate Quickly**: Both frontend and backend auto-reload
5. **Test Incrementally**: Start simple, add complexity

## 📖 Documentation

- **README.md** - Complete documentation
- **QUICKSTART.md** - Detailed quick start
- **PROJECT_SUMMARY.md** - Project overview
- **API Docs** - http://localhost:8000/docs (when running)

## 🎯 Use Cases

### Sales Team:
- Automate outbound emails
- Analyze sales calls
- Get next-action suggestions
- Track performance

### Marketing:
- Generate campaign content
- Personalize outreach
- A/B test messaging
- Monitor engagement

### Customer Success:
- Handle customer queries
- Analyze sentiment
- Suggest solutions
- Track satisfaction

## 🚀 Next Steps

1. **Explore**: Try all features in the UI
2. **Customize**: Modify agents for your use case
3. **Integrate**: Connect to your data sources
4. **Scale**: Deploy to production
5. **Optimize**: Fine-tune based on your data

## 📞 Need Help?

- Check **README.md** for detailed docs
- Review **examples/** for code samples
- Visit http://localhost:8000/docs for API reference
- Read the code comments

---

**Ready to build adaptive AI agents? Let's go! 🚀**

Start here: http://localhost:3000 (after running docker-compose up -d)
