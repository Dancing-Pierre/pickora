from functools import lru_cache
from os import getenv


class Settings:
    def __init__(self) -> None:
        self.dashscope_api_key = getenv("DASHSCOPE_API_KEY", "").strip()
        self.dashscope_model = getenv("DASHSCOPE_MODEL", "qwen-turbo").strip() or "qwen-turbo"
        self.frontend_origin = getenv("FRONTEND_ORIGIN", "http://localhost:5173").strip() or "http://localhost:5173"
        self.ai_rate_limit_per_minute = _read_int("AI_RATE_LIMIT_PER_MINUTE", 5)
        self.ai_rate_limit_per_hour = _read_int("AI_RATE_LIMIT_PER_HOUR", 30)
        self.max_request_bytes = _read_int("MAX_REQUEST_BYTES", 1024)
        self.dashscope_base_url = getenv(
            "DASHSCOPE_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        ).strip()


def _read_int(name: str, default: int) -> int:
    value = getenv(name, "").strip()
    if not value:
        return default
    try:
        parsed = int(value)
    except ValueError:
        return default
    return parsed if parsed > 0 else default


@lru_cache
def get_settings() -> Settings:
    return Settings()
