# SCRIPT PRINCIPAL DE SCRAPING
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from time import time

import pandas as pd
from tqdm import tqdm

from app.paths import DATA_S1_DIR, LOGS_S1_FILE
from scrapers.scraper_1.config import CAMPOS
from scrapers.scraper_1.utils import fetch_page, get_total_and_first_page


def collect_scraper_1_jobs() -> pd.DataFrame:
    total_records, total_pages, first_page_content = get_total_and_first_page()

    if total_records == 0:
        return pd.DataFrame(columns=CAMPOS)

    all_content = []
    all_content.extend(first_page_content)

    pages_to_fetch = range(1, total_pages)
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_page = {executor.submit(fetch_page, page): page for page in pages_to_fetch}
        for future in tqdm(as_completed(future_to_page), total=len(future_to_page), desc="PROGRESO PÁGINAS"):
            page_content = future.result()
            all_content.extend(page_content)

    df = pd.DataFrame(all_content)
    return df[[col for col in CAMPOS if col in df.columns]]


def persist_scraper_1_outputs(df: pd.DataFrame, started_at: float) -> None:
    today = datetime.now().strftime("%d-%m-%Y")
    path_log = LOGS_S1_FILE
    data_path = DATA_S1_DIR / f"{today}.csv"

    export_df = df.copy()
    export_df["id_uuid"] = [uuid.uuid4() for _ in range(len(export_df))]
    export_df["fechaActualizacion"] = datetime.now()

    data_path.parent.mkdir(parents=True, exist_ok=True)
    export_df.to_csv(data_path, index=False)
    print(f"DATOS GUARDADOS EN '{data_path}' ({len(export_df)} REGISTROS).")

    try:
        last_log = pd.read_csv(path_log)
    except FileNotFoundError:
        last_log = pd.DataFrame()

    elapsed = time() - started_at
    log_row = {
        "dep": ["all"],
        "last_date": today,
        "path_data": [data_path],
        "n_jobs": [len(export_df)],
        "time": [elapsed],
    }
    log_df = pd.concat([last_log, pd.DataFrame(log_row)], ignore_index=True)
    log_df["id_uuid"] = [uuid.uuid4() for _ in range(len(log_df))]
    path_log.parent.mkdir(parents=True, exist_ok=True)
    log_df.to_csv(path_log, index=False)

    print(f"TIEMPO DE EJECUCIÓN: {elapsed:.2f} SEGUNDOS")


def run_scraper_1(save_outputs: bool = True) -> pd.DataFrame:
    start = time()
    df = collect_scraper_1_jobs()

    if df.empty:
        print("NO HAY RESULTADOS.")
        return df

    if save_outputs:
        persist_scraper_1_outputs(df, start)

    return df


if __name__ == "__main__":
    run_scraper_1(save_outputs=True)
