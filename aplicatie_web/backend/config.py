# Standard library imports
from typing import Any, Annotated
from urllib.parse import urlparse

# Third-party imports
from pydantic import computed_field, BeforeValidator, AfterValidator, Field
from pydantic_settings import BaseSettings

# --- Defaults for Settings ---
DEFAULT_UPLOAD_DIR = "uploads"
DEFAULT_OPENAI_MODEL = "gpt-4-turbo"
DEFAULT_CORS_ORIGINS = ["http://localhost:5173"]
DEFAULT_PORT = 8081
DEFAULT_MAX_SIZE_MB = 10
DEFAULT_SUPPORTED_EXTENSIONS = ["pdf", "doc", "docx", "txt"]
DEFAULT_SUPPORTED_MIME_TYPES = [
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
]

__all__ = [
    "Settings",
    "settings",
    "DEFAULT_UPLOAD_DIR",
    "DEFAULT_OPENAI_MODEL",
    "DEFAULT_CORS_ORIGINS",
    "DEFAULT_PORT",
    "DEFAULT_MAX_SIZE_MB",
    "DEFAULT_SUPPORTED_EXTENSIONS",
    "DEFAULT_SUPPORTED_MIME_TYPES",
]

# --- Validation utilities ---
def _split_trim_nonempty(value: str | list[str] | None) -> list[str]:
    if isinstance(value, str):
        items = [p.strip() for p in (value or "").split(",")]
    else:
        items = list(value or [])
    return [p for p in items if p]

def _unique_preserve_order(seq: list[str]) -> list[str]:
    return list(dict.fromkeys(seq))

def _normalize_list(value: str | list[str] | None, *, lowercase: bool = False, strip_dot: bool = False) -> list[str]:
    items = _split_trim_nonempty(value)
    if lowercase:
        items = [s.lower() for s in items]
    if strip_dot:
        items = [s.lstrip(".") for s in items]
    return _unique_preserve_order(items)

def _normalize_path(v: str) -> str:
    return (v or "").strip().strip('\'"').rstrip("/\\")

def _forbid_path_traversal(v: str) -> str:
    if ".." in v.replace("\\", "/"):
        raise ValueError("path traversal ('..') is not allowed")
    return v

def _require_non_empty(v: str) -> str:
    if not v.strip():
        raise ValueError("must not be empty")
    return v

def _positive_int(v: int) -> int:
    if v <= 0:
        raise ValueError("must be a positive integer")
    return v

def _validate_port(v: int) -> int:
    if not (1 <= v <= 65535):
        raise ValueError("PORT must be between 1 and 65535")
    return v

def _normalize_db_url(v: Any) -> str:
    s = (v or "").strip().strip("'\"")
    if s.startswith("postgres://"):
        s = "postgresql+psycopg://" + s[len("postgres://"):]
    elif s.startswith("postgresql://"):
        s = "postgresql+psycopg://" + s[len("postgresql://"):]
    return s

def _validate_db_url(s: str) -> str:
    if not s:
        raise ValueError("DATABASE_URL cannot be empty")
    if not s.startswith("postgresql+psycopg://"):
        raise ValueError("DATABASE_URL must start with 'postgresql+psycopg://'")
    p = urlparse(s)
    if not p.netloc or "@" not in p.netloc:
        raise ValueError("DATABASE_URL must include credentials and host (user:pass@host)")
    if not p.path or p.path == "/":
        raise ValueError("DATABASE_URL must include a database name at the end")
    return s

# --- Pydantic validator wrappers ---
def _norm_cors(v: Any) -> list[str]:
    origins = _normalize_list(v, lowercase=False, strip_dot=False)
    for origin in origins:
        if not (origin.startswith(('http://', 'https://')) or origin == '*'):
            raise ValueError(f"Invalid CORS origin format: {origin}")
    return origins

def _norm_exts(v: Any) -> list[str]:
    return _normalize_list(v, lowercase=True, strip_dot=True)

def _norm_mimes(v: Any) -> list[str]:
    mime_types = _normalize_list(v, lowercase=False, strip_dot=False)
    for mime_type in mime_types:
        if "/" not in mime_type:
            raise ValueError(f"Invalid MIME type format: {mime_type}")
    return mime_types

def _norm_openai_model(v: Any) -> str:
    model = (v or "").strip()
    if not model:
        raise ValueError("OPENAI_MODEL cannot be empty")
    return model

# === Pydantic Settings model ===
class Settings(BaseSettings):
    # --- Storage paths ---
    UPLOAD_DIR: Annotated[
        str,
        BeforeValidator(_normalize_path),
        AfterValidator(_forbid_path_traversal),
        AfterValidator(_require_non_empty),
    ] = DEFAULT_UPLOAD_DIR

    # --- AI model configuration ---
    OPENAI_MODEL: Annotated[str, BeforeValidator(_norm_openai_model)] = DEFAULT_OPENAI_MODEL
    OPENAI_API_KEY: Annotated[str, Field(repr=False)]

    # --- Server configuration ---
    CORS_ORIGINS: Annotated[list[str], BeforeValidator(_norm_cors)] = DEFAULT_CORS_ORIGINS
    PORT: Annotated[int, AfterValidator(_validate_port)] = DEFAULT_PORT

    # --- Database connection ---
    DATABASE_URL: Annotated[
        str,
        BeforeValidator(_normalize_db_url),
        AfterValidator(_validate_db_url),
    ] = Field(
        default="",
        description="SQLAlchemy connection string, e.g. postgresql+psycopg://postgres:<PASS>@localhost:5432/codeflow",
    )

    # --- File upload constraints ---
    MAX_SIZE_MB: Annotated[int, AfterValidator(_positive_int)] = DEFAULT_MAX_SIZE_MB
    SUPPORTED_EXTENSIONS: Annotated[list[str], BeforeValidator(_norm_exts)] = DEFAULT_SUPPORTED_EXTENSIONS
    SUPPORTED_MIME_TYPES: Annotated[list[str], BeforeValidator(_norm_mimes)] = DEFAULT_SUPPORTED_MIME_TYPES

    # --- Computed properties ---
    @computed_field(return_type=int)
    def max_size_bytes(self) -> int:
        return self.MAX_SIZE_MB * 1024 * 1024

    # --- Pydantic configuration ---
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "forbid"
    }

# Global Settings instance (Singleton)
settings = Settings()