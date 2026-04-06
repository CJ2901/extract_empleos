from __future__ import annotations

from app.pipeline import run_enabled_scrapers
from app.settings import get_settings
from app.supabase_jobs import create_supabase_client, upsert_jobs


def main() -> None:
    settings = get_settings()
    records, results = run_enabled_scrapers(settings, save_outputs=settings.persist_local_outputs)

    if not records:
        print("No se generaron registros para subir a Supabase.")
        return

    client = create_supabase_client(settings.supabase_url, settings.supabase_service_role_key)
    upserted_count = upsert_jobs(client, records, chunk_size=settings.upsert_chunk_size)

    print("Resumen de ejecución:")
    for result in results:
        print(
            f"- {result.source}: raw={result.raw_count}, normalized={result.normalized_count}"
        )
    print(f"- jobs únicos enviados a Supabase: {upserted_count}")


if __name__ == "__main__":
    main()
