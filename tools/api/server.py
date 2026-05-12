#!/usr/bin/env python3
"""FastAPI backend for the EyeQ web frontend.

Bridges the React frontend to the existing tools.
Automatically runs in MOCK MODE when ANTHROPIC_API_KEY is not set in .env.

Run:
    uvicorn tools.api.server:app --reload --port 8000
"""

import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.api.constants import MOCK_MODE, IMAGES_DIR
from tools.api.routers import onboarding, chat, cases, flashcards, image_quiz, supervisor

app = FastAPI(title="EyeQ API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(onboarding.router, prefix="/api/onboard", tags=["Onboarding"])
app.include_router(chat.router, prefix="/api", tags=["Chat"]) # /api/chat and /api/end-session
app.include_router(cases.router, prefix="/api/cases", tags=["Cases"])
app.include_router(flashcards.router, prefix="/api/flashcards", tags=["Flashcards"])
app.include_router(image_quiz.router, prefix="/api/image-quiz", tags=["Image Quiz"])
app.include_router(supervisor.router, prefix="/api/supervisor", tags=["Supervisor"])

@app.get("/api/status")
def status():
    return {"status": "ok", "mock_mode": MOCK_MODE}

# Serve static images for the image quiz
if IMAGES_DIR.exists():
    app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("tools.api.server:app", host="0.0.0.0", port=8000, reload=True)
