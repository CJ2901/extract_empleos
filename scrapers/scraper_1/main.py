# SCRIPT PRINCIPAL DE SCRAPING
import uuid
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time
from datetime import datetime
from tqdm import tqdm
from utils import get_total_and_first_page, fetch_page
from config import CAMPOS
import os

if __name__ == "__main__":
    # INICIO DEL PROCESO
    start = time()
    today = datetime.now().strftime("%d-%m-%Y")
    
    # DEFINICIÓN DE RUTAS
    PATH_LOG = "./logs/logs.csv"
    DATA_PATH = f"../../data/scraper_1/{today}.csv"    

    total_records, total_pages, first_page_content = get_total_and_first_page()

    if total_records == 0:
        print("NO HAY RESULTADOS.")
    else:
        all_content = []
        all_content.extend(first_page_content)
        # PÁGINAS A OBTENER
        pages_to_fetch = range(1, total_pages)
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_page = {executor.submit(fetch_page, p): p for p in pages_to_fetch}
            for future in tqdm(as_completed(future_to_page), total=len(future_to_page), desc="PROGRESO PÁGINAS"):
                page_content = future.result()
                all_content.extend(page_content)
        # CREAR DATAFRAME Y FILTRAR COLUMNAS
        df = pd.DataFrame(all_content)
        df = df[[col for col in CAMPOS if col in df.columns]]
        # AGREGAR ID ÚNICO Y FECHA DE ACTUALIZACIÓN
        df["id_uuid"] = [uuid.uuid4() for _ in range(len(df))]
        df["fechaActualizacion"] = datetime.now()
        # GUARDAR CSV CON FECHA ACTUAL EN EL NOMBRE
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        df.to_csv(DATA_PATH, index=False)
        print(f"DATOS GUARDADOS EN '{DATA_PATH}' ({len(df)} REGISTROS).")
    
    # ACTUALIZAR LOGS
    try:
        last_log = pd.read_csv(PATH_LOG)
    except FileNotFoundError:
        last_log = pd.DataFrame()
    
    end = time() - start
    data_log = {
        "dep": ["all"],
        "last_date": today,
        "path_data": [DATA_PATH],
        "n_jobs": [len(df) - 10],
        "time": [end],
    }
    day_data = pd.concat([last_log, pd.DataFrame(data_log)], ignore_index=True)
    day_data["id_uuid"] = [uuid.uuid4() for _ in range(len(day_data))]
    os.makedirs(os.path.dirname(PATH_LOG), exist_ok=True)
    day_data.to_csv(PATH_LOG, index=False)
    print(f"TIEMPO DE EJECUCIÓN: {end:.2f} SEGUNDOS")
