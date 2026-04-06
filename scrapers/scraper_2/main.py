# SCRIPT PRINCIPAL
import datetime
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time

import pandas as pd
import pytz

from app.paths import DATA_S2_DIR, LOGS_S2_FILE
from scrapers.scraper_2.utils import clone_session, first_session, left_to_rigth, right_to_left

GMT5 = pytz.timezone("Etc/GMT+5")
DEPS = [str(n).zfill(2) for n in range(1, 26) if n != 15]
LIMA = "15"


def run_department(
    dep: str,
    view_state: str,
    base_session,
    connect_timeout: int,
    read_timeout: int,
) -> pd.DataFrame:
    session = clone_session(base_session)
    return left_to_rigth(
        view_state,
        dep,
        session,
        connect_timeout=connect_timeout,
        read_timeout=read_timeout,
    )


def run_lima_direction(
    right: bool,
    view_state: str,
    base_session,
    connect_timeout: int,
    read_timeout: int,
) -> pd.DataFrame:
    session = clone_session(base_session)
    if right:
        return left_to_rigth(
            view_state,
            LIMA,
            session,
            right=right,
            connect_timeout=connect_timeout,
            read_timeout=read_timeout,
        )
    return right_to_left(
        view_state,
        LIMA,
        session,
        connect_timeout=connect_timeout,
        read_timeout=read_timeout,
    )


def collect_scraper_2_jobs(
    dep_workers: int = 1,
    lima_workers: int = 1,
    connect_timeout: int = 60,
    read_timeout: int = 60,
    viewstate_retries: int = 3,
    use_selenium_fallback: bool = True,
    selenium_wait_timeout: int = 20,
) -> pd.DataFrame:
    data_list = []
    base_session, _, view_state = first_session(
        retries=viewstate_retries,
        connect_timeout=connect_timeout,
        read_timeout=read_timeout,
        use_selenium_fallback=use_selenium_fallback,
        selenium_wait_timeout=selenium_wait_timeout,
    )

    with ThreadPoolExecutor(max_workers=max(1, dep_workers)) as executor:
        futures = {
            executor.submit(
                run_department,
                dep,
                view_state,
                base_session,
                connect_timeout,
                read_timeout,
            ): dep
            for dep in DEPS
        }
        for future in as_completed(futures):
            dep = futures[future]
            try:
                data_list.append(future.result())
            except Exception as exc:
                print(f"⚠️ Error en departamento {dep}: {exc}")

    with ThreadPoolExecutor(max_workers=max(1, lima_workers)) as executor:
        futures = {
            executor.submit(
                run_lima_direction,
                side,
                view_state,
                base_session,
                connect_timeout,
                read_timeout,
            ): side
            for side in [True, False]
        }
        for future in as_completed(futures):
            side = "right" if futures[future] else "left"
            try:
                data_list.append(future.result())
            except Exception as exc:
                print(f"⚠️ Error en Lima ({side}): {exc}")

    if not data_list:
        return pd.DataFrame(columns=["posicion", "empresa", "ubicacion", "num_conv", "n_vac", "salario", "fecha_inicio", "fecha_fin"])

    return pd.concat(data_list, ignore_index=True)


def persist_scraper_2_outputs(df: pd.DataFrame, started_at: float) -> None:
    today = datetime.datetime.now(GMT5).strftime("%d-%m-%Y")
    path_log = LOGS_S2_FILE
    data_path = DATA_S2_DIR / f"{today}.csv"

    export_df = df.copy()
    export_df["id_uuid"] = [uuid.uuid4() for _ in range(len(export_df))]
    export_df["fechaActualizacion"] = datetime.datetime.now()

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


def run_scraper_2(
    save_outputs: bool = True,
    dep_workers: int = 1,
    lima_workers: int = 1,
    connect_timeout: int = 60,
    read_timeout: int = 60,
    viewstate_retries: int = 3,
    use_selenium_fallback: bool = True,
    selenium_wait_timeout: int = 20,
) -> pd.DataFrame:
    start = time()
    print(
        "scraper_2 config:"
        f" dep_workers={dep_workers},"
        f" lima_workers={lima_workers},"
        f" connect_timeout={connect_timeout},"
        f" read_timeout={read_timeout},"
        f" viewstate_retries={viewstate_retries},"
        f" selenium_fallback={use_selenium_fallback}"
    )
    df = collect_scraper_2_jobs(
        dep_workers=dep_workers,
        lima_workers=lima_workers,
        connect_timeout=connect_timeout,
        read_timeout=read_timeout,
        viewstate_retries=viewstate_retries,
        use_selenium_fallback=use_selenium_fallback,
        selenium_wait_timeout=selenium_wait_timeout,
    )

    if df.empty:
        print("NO HAY RESULTADOS EN SCRAPER 2.")
        return df

    if save_outputs:
        persist_scraper_2_outputs(df, start)

    return df


if __name__ == "__main__":
    run_scraper_2(save_outputs=True)
