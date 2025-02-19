# SCRIPT PRINCIPAL
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import first_session, left_to_rigth, right_to_left
from time import time
import pandas as pd
import pytz, datetime, uuid
import os

GMT5 = pytz.timezone("Etc/GMT+5")
today = datetime.datetime.now(GMT5).strftime("%d-%m-%Y")

DEPS = [str(n).zfill(2) for n in range(1, 26) if n != 15]
LIMA = "15"

PATH_LOG = "./logs/logs.csv"
DATA_PATH = f"../../data/scraper_2/{today}.csv"

def ejecutar(dep):
    # SCRAPING POR DEPARTAMENTO
    session, _, view_state = first_session()
    return left_to_rigth(view_state, dep, session)

def both_sides(right=True):
    # SCRAPING PARA LIMA EN AMBAS DIRECCIONES
    session, _, view_state = first_session()
    if right:
        return left_to_rigth(view_state, LIMA, session, right=right)
    else:
        return right_to_left(view_state, LIMA, session)

if __name__ == "__main__":
    start = time()
    data_list = []

    # EJECUCIÓN EN PARALELO POR DEPARTAMENTO
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(ejecutar, dep): dep for dep in DEPS}
        for future in as_completed(futures):
            data_list.append(future.result())

    # EJECUCIÓN PARA LIMA EN AMBAS DIRECCIONES
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(both_sides, side): side for side in [True, False]}
        for future in as_completed(futures):
            data_list.append(future.result())

    # UNIR RESULTADOS Y GUARDAR CSV
    data = pd.concat(data_list, ignore_index=True)
    data["id_uuid"] = [uuid.uuid4() for _ in range(len(data))]
    data["fechaActualizacion"] = datetime.datetime.now()
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    data.to_csv(DATA_PATH, index=False)
    print(f"DATOS GUARDADOS EN '{DATA_PATH}' ({len(data)} REGISTROS).")

    # ACTUALIZAR LOGS
    last_log = pd.read_csv(PATH_LOG)
    end = time() - start
    data_log = {
        "dep": ["all"],
        "last_date": today,
        "path_data": [DATA_PATH],
        "n_jobs": [len(data) - 10],
        "time": [end],
    }
    day_data = pd.concat([last_log, pd.DataFrame(data_log)], ignore_index=True)
    day_data["id_uuid"] = [uuid.uuid4() for _ in range(len(day_data))]
    day_data.to_csv(PATH_LOG, index=False)
    print(f"TIEMPO DE EJECUCIÓN: {end:.2f} SEGUNDOS")
