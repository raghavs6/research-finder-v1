from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    api_v1_prefix: str = "/api/v1"
    cors_allowed_origins: tuple[str, ...] = (
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    )
    openalex_base_url: str = "https://api.openalex.org"
    openalex_timeout_seconds: float = 5.0
    openalex_max_retries: int = 2
    openalex_retry_backoff_seconds: float = 0.2
    openalex_default_per_page: int = 100
    openalex_max_per_page: int = 200
    max_page_size: int = 25
    top_works_per_author: int = 3
    recency_window_years: int = 5
    top_venues: tuple[str, ...] = field(
        default_factory=lambda: (
            "neurips",
            "icml",
            "iclr",
            "cvpr",
            "acl",
            "emnlp",
            "kdd",
            "aaai",
            "nature",
            "science",
            "cell",
            "jama",
            "nejm",
            "lancet",
        )
    )


settings = Settings()
