from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
import numpy as np
import pandas as pd
from config import URL_DATA_SCRAPER1, URL_DATA_SCRAPER2, URL_LOGS_SCRAPER1, URL_LOGS_SCRAPER2

app = FastAPI()

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

# ENDPOINTS
@app.get("/")
def read_root():
    return {"message": "API funcionando"}

@app.get("/scraper1/jobs/{date}")
def scraper1_jobs(date: str):
    url = URL_DATA_SCRAPER1.format(date=date)
    return {"data": get_csv_from_url(url)}

@app.get("/scraper2/jobs/{date}")
def scraper2_jobs(date: str):
    url = URL_DATA_SCRAPER2.format(date=date)
    return {"data": get_csv_from_url(url)}

@app.get("/scraper1/logs")
def scraper1_logs():
    return {"data": get_csv_from_url(URL_LOGS_SCRAPER1)}

@app.get("/scraper2/logs")
def scraper2_logs():
    return {"data": get_csv_from_url(URL_LOGS_SCRAPER2)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=5173, reload=True)
