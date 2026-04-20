from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

TimeRange = Literal["hour", "day", "week", "month", "year"]

SearchCategory = Literal[
    "general",
    "news",
    "images",
    "videos",
    "music",
    "it",
    "science",
    "files",
    "social media",
]

SafeSearchLevel = Literal["0", "1", "2"]

class SearxngConfig(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = Field(default="http://searxng:8080", description="SearxNG internal URL")
    engines: str = Field(
        default="google,duckduckgo,bing,wikipedia,startpage",
        description="Comma-separated list of enabled SearxNG engines",
    )
    default_category: SearchCategory = Field(
        default="general",
        description="Default search category when none specified",
    )
    safesearch: SafeSearchLevel = Field(
        default="0",
        description="Safe search level: 0=off, 1=moderate, 2=strict",
    )
    default_limit: int = Field(default=10, ge=1, le=20, description="Max results per query")
    timeout: float = Field(default=10.0, gt=0, description="HTTP timeout in seconds")

    @field_validator("host")
    @classmethod
    def validate_host(cls, v: str) -> str:
        v = v.rstrip("/")
        if not v.startswith(("http://", "https://")):
            v = f"http://{v}"
        return v

    @property
    def engine_list(self) -> list[str]:
        return [e.strip() for e in self.engines.split(",") if e.strip()]

    @property
    def search_url(self) -> str:
        return f"{self.host}/search"

class FetchConfig(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    timeout: float = Field(default=15.0, gt=0, description="HTTP timeout in seconds")
    max_content_length: int = Field(
        default=10000,
        ge=1000,
        le=100000,
        description="Max characters to extract from a page",
    )
    token_budget: int = Field(
        default=8000,
        ge=1000,
        le=128000,
        description="Approximate token budget for extracted content",
    )
    max_redirects: int = Field(default=5, ge=0, le=10, description="Max HTTP redirects to follow")
    max_concurrent_browsers: int = Field(
        default=2, 
        ge=1, 
        le=10, 
        description="Max concurrent browser instances for nodriver fallback"
    )

class ServerConfig(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = Field(default="0.0.0.0", description="Host address to bind")
    port: int = Field(default=8000, ge=1, le=65535, description="Port for SSE endpoint")
    api_key: str = Field(default="", description="Optional API key for MCP server access control")
    default_search_type: str = Field(
        default="auto",
        description="Default search type: instant, fast, auto, deep_lite, deep, deep_reasoning",
    )

@lru_cache(maxsize=1)
def get_searxng_config() -> SearxngConfig:
    return SearxngConfig()

@lru_cache(maxsize=1)
def get_fetch_config() -> FetchConfig:
    return FetchConfig()

@lru_cache(maxsize=1)
def get_server_config() -> ServerConfig:
    return ServerConfig()
