from app.middleware.request_timing import RequestTimingMiddleware
from fastapi import FastAPI


def register_middlewares(app: FastAPI) -> None:
    if not any(m.cls is RequestTimingMiddleware for m in app.user_middleware):
        app.add_middleware(RequestTimingMiddleware)
