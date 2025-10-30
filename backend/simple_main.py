from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the API routers
from app.api import agents
try:
    from app.api import voice
    VOICE_API_AVAILABLE = True
except ImportError:
    VOICE_API_AVAILABLE = False
    print("Voice API not available")

app = FastAPI(
    title="Adaptive AI Agent System - Local AI",
    description="Multi-agent AI system with local intelligence (no API keys required)",
    version="1.0.0",
    debug=True
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the agents router
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])

# Include voice router if available
if VOICE_API_AVAILABLE:
    app.include_router(voice.router, prefix="/api/voice", tags=["voice"])

@app.get("/")
async def root():
    return {
        "message": "Adaptive AI Agent System is running with Local AI!", 
        "status": "healthy",
        "features": [
            "Sales Agent - Lead qualification, objection handling, sales strategy",
            "Email Agent - Cold outreach, email sequences, subject lines", 
            "Auto Agent - Intelligent routing and general business advice"
        ],
        "no_api_keys_required": True
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": "development",
        "ai_type": "local_intelligence",
        "agents_available": ["sales", "email", "auto"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)