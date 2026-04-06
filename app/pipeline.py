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


def run_enabled_scrapers(settings: Settings, save_outputs: bool) -> tuple[list[dict], list[ScraperResult]]:
    all_records: list[dict] = []
    results: list[ScraperResult] = []

    if settings.run_scraper_1:
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

    if settings.run_scraper_2:
        scraper_2_df = run_scraper_2(save_outputs=save_outputs)
        normalized = normalize_scraper_2(scraper_2_df)
        all_records.extend(normalized)
        results.append(
            ScraperResult(
                source="scraper_2",
                raw_count=len(scraper_2_df),
                normalized_count=len(normalized),
            )
        )

    return dedupe_jobs(all_records), results
