from __future__ import annotations

from app.pipeline import run_enabled_scrapers
from app.settings import get_settings
from app.supabase_jobs import create_supabase_client, upsert_jobs


def main() -> None:
    settings = get_settings()
    records, results = run_enabled_scrapers(settings, save_outputs=settings.persist_local_outputs)
    had_success = any(result.status == "ok" for result in results)

    if not records:
        print("Resumen de ejecución:")
        for result in results:
            status_suffix = f" status={result.status}"
            print(
                f"- {result.source}: raw={result.raw_count}, normalized={result.normalized_count}{status_suffix}"
            )
            if result.error:
                print(f"  error: {result.error}")

        if had_success:
            print("No se generaron registros para subir a Supabase.")
            return

        print("No se generaron registros para subir a Supabase.")
        raise SystemExit(1)

    client = create_supabase_client(settings.supabase_url, settings.supabase_service_role_key)
    upserted_count = upsert_jobs(client, records, chunk_size=settings.upsert_chunk_size)

    print("Resumen de ejecución:")
    for result in results:
        status_suffix = f" status={result.status}"
        print(
            f"- {result.source}: raw={result.raw_count}, normalized={result.normalized_count}{status_suffix}"
        )
        if result.error:
            print(f"  error: {result.error}")
    print(f"- jobs únicos enviados a Supabase: {upserted_count}")


if __name__ == "__main__":
    main()
