from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.detector import detect
from app.schemas import DetectRequest, DetectResponse, DetectResult, MIN_TEXT_LENGTH

app = FastAPI(title="AI Detector")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Fixed-window per-IP limiter. Health checks are exempt."""

    def __init__(self, app, requests_per_minute: int):
        super().__init__(app)
        self.requests_per_minute = max(1, requests_per_minute)
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/api/health":
            return await call_next(request)

        client = request.client.host if request.client else "unknown"
        now = time.monotonic()
        window_start = now - 60.0
        bucket = self._hits[client]
        while bucket and bucket[0] < window_start:
            bucket.popleft()
        if len(bucket) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Rate limit exceeded ({self.requests_per_minute}/min). Retry later."
                },
            )
        bucket.append(now)
        return await call_next(request)


app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.rate_limit_per_minute)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "dashscope_configured": bool(settings.qwen_api_key.strip()),
        "version": settings.app_version,
    }


@app.post("/api/detect", response_model=DetectResponse)
def detect_api(req: DetectRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="文本不能为空")

    text_length = len(text)
    if text_length < MIN_TEXT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"文本长度不足，至少需要 {MIN_TEXT_LENGTH} 字，当前 {text_length} 字",
        )

    result = detect(text)
    return DetectResponse(result=DetectResult(**result))
