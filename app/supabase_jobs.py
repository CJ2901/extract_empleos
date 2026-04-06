from __future__ import annotations

from typing import Any

from supabase import Client, ClientOptions, create_client


def create_supabase_client(supabase_url: str, service_role_key: str) -> Client:
    return create_client(
        supabase_url,
        service_role_key,
        options=ClientOptions(auto_refresh_token=False, persist_session=False),
    )


def chunk_records(records: list[dict[str, Any]], chunk_size: int) -> list[list[dict[str, Any]]]:
    return [records[index : index + chunk_size] for index in range(0, len(records), chunk_size)]


def upsert_jobs(client: Client, records: list[dict[str, Any]], chunk_size: int = 500) -> int:
    total = 0
    for chunk in chunk_records(records, chunk_size):
        client.table("jobs").upsert(chunk, on_conflict="job_uid").execute()
        total += len(chunk)
    return total
