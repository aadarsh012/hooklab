from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import analyze

app = FastAPI(title="HookLab API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router)
