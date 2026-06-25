from functools import lru_cache

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import ClientDisconnect

from .config import Settings, get_settings
from .dashscope_client import generate_dashscope_options
from .rate_limit import RateLimiter
from .schemas import GenerateOptionsRequest, GenerateOptionsResponse


@lru_cache
def get_limiter() -> RateLimiter:
    settings = get_settings()
    return RateLimiter(settings.ai_rate_limit_per_minute, settings.ai_rate_limit_per_hour)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Pickora API", version="0.1.0")

    allowed_origins = [settings.frontend_origin]
    if settings.frontend_origin != "http://localhost:5173":
        allowed_origins.append("http://localhost:5173")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @app.middleware("http")
    async def reject_large_requests(request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > settings.max_request_bytes:
                    return JSONResponse(status_code=413, content={"detail": "请求内容过大。"})
            except ValueError:
                return JSONResponse(status_code=400, content={"detail": "请求头格式不正确。"})
        elif request.method in {"POST", "PUT", "PATCH"}:
            try:
                body = await request.body()
            except ClientDisconnect:
                return JSONResponse(status_code=400, content={"detail": "请求读取失败。"})
            if len(body) > settings.max_request_bytes:
                return JSONResponse(status_code=413, content={"detail": "请求内容过大。"})
        return await call_next(request)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/generate-options", response_model=GenerateOptionsResponse)
    async def generate_options(
        payload: GenerateOptionsRequest,
        request: Request,
        limiter: RateLimiter = Depends(get_limiter),
        current_settings: Settings = Depends(get_settings),
    ) -> GenerateOptionsResponse:
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",", 1)[0].strip() or client_ip

        if not limiter.allow(client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="AI 生成太频繁了，稍等一下再试，或者先手动输入选项。",
            )

        options = await generate_dashscope_options(payload.category, current_settings)
        return GenerateOptionsResponse(category=payload.category, options=options)

    return app


app = create_app()
