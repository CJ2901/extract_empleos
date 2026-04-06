from __future__ import annotations

import hashlib
import re
import unicodedata
from datetime import datetime, timezone
from typing import Any

import pandas as pd


def clean_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None

    text = str(value).strip()
    if not text:
        return None

    return re.sub(r"\s+", " ", text)


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_value.lower()
    return re.sub(r"[^a-z0-9]+", "_", lowered).strip("_")


def build_hash(parts: list[str | None]) -> str:
    raw = "||".join(part or "" for part in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def parse_datetime(value: Any, formats: list[str]) -> str | None:
    text = clean_text(value)
    if not text:
        return None

    for fmt in formats:
        try:
            parsed = datetime.strptime(text, fmt)
            return parsed.replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            continue
    return None


def current_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def fallback_job_url(source: str, job_uid: str, external_id: str | None) -> str:
    safe_external_id = external_id or job_uid
    return f"https://jobs.nanocv.local/{source}/{slugify(safe_external_id)}"


def normalize_scraper_1(df: pd.DataFrame) -> list[dict[str, Any]]:
    scraped_at = current_timestamp()
    records: list[dict[str, Any]] = []

    for row in df.to_dict(orient="records"):
        external_id = clean_text(row.get("id"))
        source = slugify(clean_text(row.get("portal")) or "bumeran")
        title = clean_text(row.get("titulo"))
        company = clean_text(row.get("empresa")) or "Confidencial"
        location = clean_text(row.get("localizacion"))
        modality = clean_text(row.get("modalidadTrabajo"))
        description = clean_text(row.get("detalle"))

        job_uid = f"{source}:{external_id}" if external_id else build_hash([source, title, company, location])[:40]
        content_hash = build_hash(
            [
                source,
                external_id,
                title,
                company,
                location,
                modality,
                description,
                clean_text(row.get("tipoTrabajo")),
                clean_text(row.get("cantidadVacantes")),
            ]
        )

        records.append(
            {
                "job_uid": job_uid,
                "source": source,
                "external_id": external_id,
                "title": title,
                "company": company,
                "location": location,
                "modality": modality,
                "seniority": clean_text(row.get("tipoTrabajo")),
                "salary_text": None,
                "description": description,
                "requirements_text": description,
                "job_url": fallback_job_url(source, job_uid, external_id),
                "posted_at": parse_datetime(
                    row.get("fechaHoraPublicacion"),
                    ["%d-%m-%Y %H:%M:%S", "%d-%m-%Y"],
                ),
                "scraped_at": scraped_at,
                "last_seen_at": scraped_at,
                "is_active": True,
                "content_hash": content_hash,
                "updated_at": scraped_at,
            }
        )

    return records


def normalize_scraper_2(df: pd.DataFrame) -> list[dict[str, Any]]:
    scraped_at = current_timestamp()
    records: list[dict[str, Any]] = []

    for row in df.to_dict(orient="records"):
        source = "servir"
        title = clean_text(row.get("posicion"))
        company = clean_text(row.get("empresa"))
        location = clean_text(row.get("ubicacion"))
        external_id = clean_text(row.get("num_conv"))
        salary_text = clean_text(row.get("salario"))
        description = clean_text(row.get("num_conv"))
        requirements = clean_text(row.get("n_vac"))

        unique_suffix = external_id or build_hash([title, company, location, clean_text(row.get("fecha_inicio"))])[:24]
        job_uid = f"{source}:{slugify(unique_suffix)}"
        content_hash = build_hash(
            [
                source,
                external_id,
                title,
                company,
                location,
                salary_text,
                clean_text(row.get("fecha_inicio")),
                clean_text(row.get("fecha_fin")),
            ]
        )

        records.append(
            {
                "job_uid": job_uid,
                "source": source,
                "external_id": external_id,
                "title": title,
                "company": company,
                "location": location,
                "modality": "Presencial",
                "seniority": None,
                "salary_text": salary_text,
                "description": description,
                "requirements_text": requirements,
                "job_url": fallback_job_url(source, job_uid, external_id),
                "posted_at": parse_datetime(row.get("fecha_inicio"), ["%d/%m/%Y"]),
                "scraped_at": scraped_at,
                "last_seen_at": scraped_at,
                "is_active": True,
                "content_hash": content_hash,
                "updated_at": scraped_at,
            }
        )

    return records


def dedupe_jobs(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: dict[str, dict[str, Any]] = {}
    for record in records:
        deduped[record["job_uid"]] = record
    return list(deduped.values())
