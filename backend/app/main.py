from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.api import agents, voice, analytics, workflows

app = FastAPI(
    title="Adaptive AI Agent System",
    description="Multi-agent AI system with real-time voice and adaptive learning",
    version="1.0.0",
    debug=settings.DEBUG
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(voice.router, prefix="/api/voice", tags=["voice"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(workflows.router, prefix="/api/workflows", tags=["workflows"])


@app.on_event("startup")
async def startup_event():
    logger.info("Starting Adaptive AI Agent System...")
    logger.info(f"Environment: {settings.ENV}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Adaptive AI Agent System...")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENV
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(levelname)s: %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
            },
            "loggers": {
                "uvicorn": {"handlers": ["default"], "level": "INFO"},
                "uvicorn.error": {"level": "INFO"},
                "uvicorn.access": {"level": "WARNING"},
            },
        }
    )
