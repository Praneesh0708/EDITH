from fastapi import FastAPI

from interview import router as interview_router


app = FastAPI(
    title="EDITH AI Interview System",
    description="AI-powered adaptive interview analyzer",
    version="1.0.0"
)


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