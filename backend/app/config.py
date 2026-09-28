import os
from dotenv import load_dotenv

load_dotenv()


def _csv_env(name: str, default: str) -> list[str]:
    raw = os.getenv(name, default).strip()
    if raw == "*":
        return ["*"]
    return [part.strip() for part in raw.split(",") if part.strip()]


class Settings:
    qwen_model = os.getenv("QWEN_MODEL", "qwen-plus")
    qwen_api_key = os.getenv("DASHSCOPE_API_KEY", "")
    qwen_timeout = float(os.getenv("QWEN_TIMEOUT", "15"))
    detect_temperature = float(os.getenv("DETECT_TEMPERATURE", "0.2"))
    # 多粒度检测配置
    enable_multi_granularity = os.getenv("ENABLE_MULTI_GRANULARITY", "true").lower() == "true"
    sentence_analysis_threshold = float(os.getenv("SENTENCE_ANALYSIS_THRESHOLD", "0.4"))  # 文档级得分超过此值才进行句子级分析（降低阈值，让更多文本进入句子级检测）
    # 反向检测：当判断为人类时，也进行句子级验证
    enable_reverse_check = os.getenv("ENABLE_REVERSE_CHECK", "true").lower() == "true"
    # Release-ready defaults: browser origins + simple API rate limit
    cors_origins = _csv_env(
        "CORS_ORIGINS",
        "http://localhost:8080,http://127.0.0.1:8080,http://localhost:5173,http://127.0.0.1:5173",
    )
    rate_limit_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    app_version = os.getenv("APP_VERSION", os.getenv("GIT_SHA", "dev"))


settings = Settings()
