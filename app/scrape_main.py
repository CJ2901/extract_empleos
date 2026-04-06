from __future__ import annotations

from app.pipeline import run_enabled_scrapers
from app.settings import get_settings


def main() -> None:
    settings = get_settings()
    _, results = run_enabled_scrapers(settings, save_outputs=True)

    print("Resumen de scraping:")
    for result in results:
        print(f"- {result.source}: raw={result.raw_count}, normalized={result.normalized_count}")


if __name__ == "__main__":
    main()
