from app.core.config import get_settings
from app.middleware.request_timing import RequestTimingMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def register_middlewares(app: FastAPI) -> None:
    settings = get_settings()

    # CORS middleware - must be added first
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request timing middleware
    app.add_middleware(RequestTimingMiddleware)
