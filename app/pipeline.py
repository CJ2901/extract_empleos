from __future__ import annotations

from dataclasses import dataclass
from app.normalizers import dedupe_jobs, normalize_scraper_1, normalize_scraper_2
from app.settings import Settings
from scrapers.scraper_1.main import run_scraper_1
from scrapers.scraper_2.main import run_scraper_2


@dataclass
class ScraperResult:
    source: str
    raw_count: int
    normalized_count: int
    status: str = "ok"
    error: str | None = None


def run_enabled_scrapers(settings: Settings, save_outputs: bool) -> tuple[list[dict], list[ScraperResult]]:
    all_records: list[dict] = []
    results: list[ScraperResult] = []

    if settings.run_scraper_1:
        try:
            scraper_1_df = run_scraper_1(save_outputs=save_outputs)
            normalized = normalize_scraper_1(scraper_1_df)
            all_records.extend(normalized)
            results.append(
                ScraperResult(
                    source="scraper_1",
                    raw_count=len(scraper_1_df),
                    normalized_count=len(normalized),
                )
            )
        except Exception as exc:
            print(f"⚠️ scraper_1 falló: {exc}")
            results.append(
                ScraperResult(
                    source="scraper_1",
                    raw_count=0,
                    normalized_count=0,
                    status="error",
                    error=str(exc),
                )
            )

    if settings.run_scraper_2:
        try:
            scraper_2_df = run_scraper_2(
                save_outputs=save_outputs,
                dep_workers=settings.scraper_2_dep_workers,
                lima_workers=settings.scraper_2_lima_workers,
                connect_timeout=settings.scraper_2_connect_timeout,
                read_timeout=settings.scraper_2_read_timeout,
                viewstate_retries=settings.scraper_2_viewstate_retries,
                use_selenium_fallback=settings.scraper_2_use_selenium_fallback,
                selenium_wait_timeout=settings.scraper_2_selenium_wait_timeout,
            )
            normalized = normalize_scraper_2(scraper_2_df)
            all_records.extend(normalized)
            results.append(
                ScraperResult(
                    source="scraper_2",
                    raw_count=len(scraper_2_df),
                    normalized_count=len(normalized),
                )
            )
        except Exception as exc:
            print(f"⚠️ scraper_2 falló: {exc}")
            results.append(
                ScraperResult(
                    source="scraper_2",
                    raw_count=0,
                    normalized_count=0,
                    status="error",
                    error=str(exc),
                )
            )

    return dedupe_jobs(all_records), results
