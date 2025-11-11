from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.database import engine, Base
from app.api.routes import auth, reading, writing, quests, dashboard, settings, staking

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Web3 Education Platform API",
    description="API for IELTS/TOEFL test preparation with AI and Web3",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(reading.router, prefix="/api")
app.include_router(writing.router, prefix="/api")
app.include_router(quests.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(staking.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "Web3 Education Platform API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    from app.config.settings import settings

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
    )
