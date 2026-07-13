import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import analyze

app = FastAPI(title="HookLab API")

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router)
