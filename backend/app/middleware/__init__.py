from fastapi import FastAPI

from app.middleware.request_timing import RequestTimingMiddleware


def register_middlewares(app: FastAPI) -> None:
    if not any(isinstance(m, RequestTimingMiddleware) for m in app.user_middleware):
        app.add_middleware(RequestTimingMiddleware)

