# FUNCIONES AUXILIARES DE SCRAPING
import requests
from config import BASE_URL, HEADERS, DATA_BODY, PAGE_SIZE

def get_total_and_first_page():
    # OBTIENE TOTAL, PÁGINAS Y PRIMERA PÁGINA
    url = f"{BASE_URL}?pageSize={PAGE_SIZE}&page=0"
    resp = requests.post(url, headers=HEADERS, json=DATA_BODY)
    resp.raise_for_status()
    resp_json = resp.json()
    total_records = resp_json.get("total", 0)
    content = resp_json.get("content", [])
    total_pages = total_records // PAGE_SIZE
    if total_records % PAGE_SIZE != 0:
        total_pages += 1
    return total_records, total_pages, content

def fetch_page(page_number):
    # OBTIENE CONTENIDO DE UNA PÁGINA
    url = f"{BASE_URL}?pageSize={PAGE_SIZE}&page={page_number}"
    resp = requests.post(url, headers=HEADERS, json=DATA_BODY)
    resp.raise_for_status()
    resp_json = resp.json()
    return resp_json.get("content", [])
