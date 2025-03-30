from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
import numpy as np
import pandas as pd
import os
from glob import glob
from datetime import datetime
from config import URL_DATA_SCRAPER1, URL_DATA_SCRAPER2, URL_LOGS_SCRAPER1, URL_LOGS_SCRAPER2

app = FastAPI()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# CONFIG. DE CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # PERMITIR TODOS LOS ORÍGENES
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_csv_from_url(url: str):
    try:
        df = pd.read_csv(url)
        # REEMPLAZAR NAN E INF
        df = df.replace({np.nan: None, np.inf: None, -np.inf: None})
        data = df.to_dict(orient="records")
        return jsonable_encoder(data)
    except Exception as e:
        return {"error": str(e)}

def get_latest_date_from_data(folder: str) -> str:
    absolute_folder = os.path.join(BASE_DIR, folder)
    print(f"Buscando archivos CSV en: {absolute_folder}")
    files = glob(os.path.join(absolute_folder, "*.csv"))
    fechas = []
    for file in files:
        nombre_archivo = os.path.basename(file)
        nombre, _ = os.path.splitext(nombre_archivo)
        try:
            fecha = datetime.strptime(nombre, "%d-%m-%Y")
            fechas.append(fecha)
        except ValueError:
            continue
    if not fechas:
        return None
    fecha_mas_reciente = max(fechas)
    return fecha_mas_reciente.strftime("%d-%m-%Y")

# ENDPOINTS
@app.get("/")
def read_root():
    return {"message": "API funcionando"}

@app.get("/scraper1/logs")
def scraper1_logs():
    return {"data": get_csv_from_url(URL_LOGS_SCRAPER1)}

@app.get("/scraper2/logs")
def scraper2_logs():
    return {"data": get_csv_from_url(URL_LOGS_SCRAPER2)}

@app.get("/scraper1/jobs/latest")
def scraper1_jobs_latest():
    latest_date = get_latest_date_from_data(os.path.join("data", "scraper_1"))
    if latest_date is None:
        return {"error": "No se encontraron archivos CSV en data/scraper_1"}
    return scraper1_jobs(latest_date)

@app.get("/scraper2/jobs/latest")
def scraper2_jobs_latest():
    latest_date = get_latest_date_from_data(os.path.join("data", "scraper_2"))
    if latest_date is None:
        return {"error": "No se encontraron archivos CSV en data/scraper_2"}
    return scraper2_jobs(latest_date)

@app.get("/scraper1/jobs/{date}")
def scraper1_jobs(date: str):
    url = URL_DATA_SCRAPER1.format(date=date)
    return {"data": get_csv_from_url(url)}

@app.get("/scraper2/jobs/{date}")
def scraper2_jobs(date: str):
    url = URL_DATA_SCRAPER2.format(date=date)
    print(f"URL: {url}")
    return {"data": get_csv_from_url(url)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=5173, reload=True)
