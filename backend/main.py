from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.interview import router as interview_router


app = FastAPI(
    title="EDITH AI Interview System",
    description="AI-powered adaptive interview analyzer",
    version="1.0.0"
)


# --------------------------------
# CORS Configuration
# --------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------
# API STATUS
# --------------------------------

@app.get("/api/status")
def api_status():
    return {
        "backend": "online",
        "status": "success"
    }


# --------------------------------
# Interview Router
# --------------------------------

app.include_router(interview_router)


# --------------------------------
# Root Endpoint
# --------------------------------

@app.get("/")
def root():
    return {
        "status": "success",
        "message": "EDITH Backend is running"
    }