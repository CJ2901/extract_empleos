from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def load_dotenv(dotenv_path: Path | None = None) -> None:
    env_path = dotenv_path or BASE_DIR / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        if key.startswith("export "):
            key = key.removeprefix("export ").strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value.strip())


@dataclass(frozen=True)
class Settings:
    supabase_url: str
    supabase_service_role_key: str
    run_scraper_1: bool
    run_scraper_2: bool
    persist_local_outputs: bool
    upsert_chunk_size: int
    scraper_2_dep_workers: int
    scraper_2_lima_workers: int
    scraper_2_request_timeout: int
    scraper_2_viewstate_retries: int
    scraper_2_use_selenium_fallback: bool
    scraper_2_selenium_wait_timeout: int


def get_settings() -> Settings:
    load_dotenv()

    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()

    if not supabase_url:
        raise RuntimeError("Missing required environment variable: SUPABASE_URL")
    if not supabase_service_role_key:
        raise RuntimeError("Missing required environment variable: SUPABASE_SERVICE_ROLE_KEY")

    return Settings(
        supabase_url=supabase_url,
        supabase_service_role_key=supabase_service_role_key,
        run_scraper_1=env_bool("RUN_SCRAPER_1", True),
        run_scraper_2=env_bool("RUN_SCRAPER_2", True),
        persist_local_outputs=env_bool("PERSIST_LOCAL_OUTPUTS", False),
        upsert_chunk_size=env_int("UPSERT_CHUNK_SIZE", 500),
        scraper_2_dep_workers=env_int("SCRAPER_2_DEP_WORKERS", 1),
        scraper_2_lima_workers=env_int("SCRAPER_2_LIMA_WORKERS", 1),
        scraper_2_request_timeout=env_int("SCRAPER_2_REQUEST_TIMEOUT", 30),
        scraper_2_viewstate_retries=env_int("SCRAPER_2_VIEWSTATE_RETRIES", 3),
        scraper_2_use_selenium_fallback=env_bool("SCRAPER_2_USE_SELENIUM_FALLBACK", True),
        scraper_2_selenium_wait_timeout=env_int("SCRAPER_2_SELENIUM_WAIT_TIMEOUT", 20),
    )
