# Quick Start Guide

## Get Started in 5 Minutes

### 1. Prerequisites Check

```bash
# Check Python version (need 3.11+)
python --version

# Check Node.js version (need 18+)
node --version

# Check if Docker is installed (optional)
docker --version
```

### 2. Quick Setup with Docker (Easiest)

```bash
# Clone and enter directory
cd adaptive-ai-agent-system

# Copy environment files
cp backend/.env.example backend/.env

# Edit backend/.env and add your API keys:
# - OPENAI_API_KEY
# - ANTHROPIC_API_KEY
# - PINECONE_API_KEY
# - LIVEKIT credentials

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### 3. Manual Setup (More Control)

#### Step 1: Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Start backend
python -m app.main
```

#### Step 2: Frontend (New Terminal)

```bash
cd frontend

# Install dependencies
npm install

# Setup environment
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start frontend
npm run dev
```

### 4. First Steps

1. **Open the UI**: Navigate to http://localhost:3000

2. **Test Agents**:
   - Go to "Agent Orchestration"
   - Enter a task like: "Draft an email to a prospect about our AI solution"
   - Click "Execute Task"

3. **Generate Email**:
   - Go to "Email Campaign Generator"
   - Fill in prospect information
   - Click "Generate Email"

4. **Check Analytics**:
   - Go to "Analytics Dashboard"
   - View agent performance metrics

### 5. API Testing

```bash
# Health check
curl http://localhost:8000/health

# Execute agent task
curl -X POST http://localhost:8000/api/agents/execute \
  -H "Content-Type: application/json" \
  -d '{"task": "Analyze sales data", "agent_type": "sales"}'

# Generate email
curl -X POST http://localhost:8000/api/agents/generate-email \
  -H "Content-Type: application/json" \
  -d '{
    "prospect_name": "John Doe",
    "prospect_company": "Acme Corp",
    "prospect_role": "VP Sales"
  }'
```

## Minimal Configuration

### Required API Keys

1. **OpenAI** (for LLMs): https://platform.openai.com/api-keys
2. **Anthropic** (optional): https://console.anthropic.com/
3. **Pinecone** (for vector search): https://www.pinecone.io/

### Optional Services

- **LiveKit** (for voice): https://livekit.io/
- **LangSmith** (for tracing): https://smith.langchain.com/

## Testing Without Full Setup

You can test core functionality without all services:

```python
# Test agents locally
cd backend
python

>>> from app.agents.adaptive_agent import SalesAgent
>>> agent = SalesAgent()
>>> # This will work with just OpenAI API key
```

## Common Issues

### Issue: Import errors
**Solution**: Make sure virtual environment is activated

### Issue: Database connection errors
**Solution**: 
- Using Docker: `docker-compose up -d postgres redis clickhouse`
- Manual: Install and start PostgreSQL, Redis, ClickHouse

### Issue: Port already in use
**Solution**: Change ports in docker-compose.yml or stop conflicting services

## Next Steps

1. **Explore the code**: Start with `backend/app/agents/adaptive_agent.py`
2. **Customize agents**: Modify agent behavior in `adaptive_agent.py`
3. **Add tools**: Extend agent capabilities by adding new tools
4. **Setup workflows**: Configure Temporal workflows for automation
5. **Deploy**: Follow deployment guide in README.md

## Development Workflow

```bash
# Backend development
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m app.main

# Frontend development
cd frontend
npm run dev

# Both watch for changes and auto-reload
```

## Getting Help

- **Documentation**: See README.md for detailed info
- **API Docs**: http://localhost:8000/docs (when backend is running)
- **Examples**: Check the `examples/` directory (coming soon)

Happy coding! 🚀
