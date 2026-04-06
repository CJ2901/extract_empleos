# FUNCIONES DE SCRAPING Y AUXILIARES
import os
import re
import time
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup as bsoup
import warnings
from bs4 import XMLParsedAsHTMLWarning
from tqdm import tqdm
from scrapers.scraper_2.config import URL, HEADERS, share_payload, first_page, next_page, last_page, prev_page

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# --- FUNC. AUXILIARES ---
def limpiar_espacios(texto):
    # LIMPIA ESPACIOS EXTRA
    texto = re.sub(r"\s{2,}", " ", texto)
    texto = re.sub(r"\t+", " ", texto)
    texto = re.sub(r"\n+", " ", texto)
    return texto.strip()

def total_numbers(texto):
    # EXTRAER NÚMEROS
    numeros = re.findall(r"\d+", texto)
    return [int(num) for num in numeros]

def goto_dep_payload(view_state_value, dep_search):
    # PAYLOAD BASE CON DEP Y VIEWSTATE
    payload = share_payload.copy()
    payload.update({
        "javax.faces.ViewState": view_state_value,
        "frmLstOfertsLabo:cboDep_input": dep_search,
    })
    return payload

def goto_first_dep_page_payload(view_state_value, dep_search):
    # PAYLOAD PARA PRIMERA PÁGINA
    payload = goto_dep_payload(view_state_value, dep_search)
    payload.update(first_page)
    return payload

def goto_next_page_payload(view_state_value, dep_search):
    # PAYLOAD PARA SIGUIENTE PÁGINA
    payload = goto_dep_payload(view_state_value, dep_search)
    payload.update(next_page)
    return payload

def goto_last_page_payload(view_state_value, dep_search):
    # PAYLOAD PARA ÚLTIMA PÁGINA
    payload = goto_dep_payload(view_state_value, dep_search)
    payload.update(last_page)
    return payload

def goto_prev_page_payload(view_state_value, dep_search):
    # PAYLOAD PARA PÁGINA PREVIA
    payload = goto_dep_payload(view_state_value, dep_search)
    payload.update(prev_page)
    return payload

# --- FUNCIONES DE SCRAPING ---
def get_view_state(soup):
    view_state_input = soup.find("input", {"name": "javax.faces.ViewState"})
    if view_state_input is None:
        print("DEBUG: No se encontró el input con name 'javax.faces.ViewState'.")
        # Puedes imprimir parte del HTML para ver qué se está recibiendo (ten cuidado con el tamaño)
        print("DEBUG: Inicio del contenido recibido:", soup.prettify()[:1000])
        raise ValueError("No se encontró 'javax.faces.ViewState' en la respuesta HTML.")
    return view_state_input.get("value")


def _request_session(url=URL, head=HEADERS, retries=3, request_timeout=30):
    session = requests.Session()
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            response = session.get(url, headers=head, timeout=request_timeout)
            response.raise_for_status()
            soup = bsoup(response.content, features="lxml")
            view_state = get_view_state(soup)
            return session, soup, view_state
        except Exception as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(1.5 * attempt)
    raise RuntimeError(f"No se pudo obtener el ViewState con requests: {last_error}")


def _selenium_session(url=URL, head=HEADERS, request_timeout=30, wait_timeout=20):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-background-networking")
    options.add_argument(f'--user-agent={head.get("User-Agent", "")}')
    options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_binary = os.getenv("CHROME_BIN")
    if chrome_binary:
        options.binary_location = chrome_binary

    chrome_driver_path = os.getenv("CHROMEDRIVER_BIN", "/usr/bin/chromedriver")
    service = Service(executable_path=chrome_driver_path)

    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(max(wait_timeout + 10, request_timeout))

    try:
        driver.get(url)
        wait = WebDriverWait(driver, wait_timeout)
        element = wait.until(EC.presence_of_element_located((By.NAME, "javax.faces.ViewState")))
        view_state = element.get_attribute("value")
    except Exception as e:
        page_source_snippet = driver.page_source[:1000]
        driver.quit()
        raise Exception(f"Error al obtener el ViewState con Selenium: {e}. Page source snippet: {page_source_snippet}")

    session = requests.Session()
    for cookie in driver.get_cookies():
        session.cookies.set(cookie["name"], cookie["value"])

    html = driver.page_source
    soup = bsoup(html, features="lxml")
    driver.quit()

    return session, soup, view_state


def first_session(
    url=URL,
    head=HEADERS,
    retries=3,
    request_timeout=30,
    use_selenium_fallback=True,
    selenium_wait_timeout=20,
):
    try:
        return _request_session(
            url=url,
            head=head,
            retries=retries,
            request_timeout=request_timeout,
        )
    except Exception as request_error:
        if not use_selenium_fallback:
            raise RuntimeError(str(request_error)) from request_error

        last_error = request_error
        for attempt in range(1, retries + 1):
            try:
                return _selenium_session(
                    url=url,
                    head=head,
                    request_timeout=request_timeout,
                    wait_timeout=selenium_wait_timeout,
                )
            except Exception as selenium_error:
                last_error = selenium_error
                if attempt < retries:
                    time.sleep(2 * attempt)

        raise RuntimeError(str(last_error)) from last_error


def goto_page(data, session, request_timeout=30):
    # PETICIÓN POST CON PAYLOAD
    response = session.post(url=URL, headers=HEADERS, data=data, timeout=request_timeout)
    response.raise_for_status()
    return response.content

def souper(content):
    # CONVERTIR HTML A SOUP
    return bsoup(content, features="lxml")

def get_label_page(soup):
    # OBTENER ETIQUETA DE PÁGINA
    return soup.find("label", class_="control-label btn-paginator-cnt").text

def convert_in_df(soup):
    # CONVERTIR INFO A DATAFRAME
    jobs = soup.find_all("div", class_="cuadro-vacantes")
    info = []
    for job in jobs:
        pos = job.find("div", class_="titulo-vacante").get_text(strip=True).replace("\n", "")
        spans = job.find_all("span", class_="detalle-sp")
        details = [limpiar_espacios(span.get_text(strip=True)) for span in spans]
        info.append([pos] + details)
    return pd.DataFrame(info, columns=["posicion","empresa","ubicacion","num_conv","n_vac","salario","fecha_inicio","fecha_fin"])

def data_souper(content):
    # PROCESAR CONTENIDO DE PÁGINA
    soup = souper(content)
    page_text = get_label_page(soup)
    _, total = total_numbers(page_text)
    data = convert_in_df(soup)
    return data, total

def go_first_page(view_state, dep, session, request_timeout=30):
    # OBTENER PRIMERA PÁGINA
    payload = goto_first_dep_page_payload(view_state, dep)
    content = goto_page(payload, session, request_timeout=request_timeout)
    data,total_pages = data_souper(content)
    return data,total_pages

def go_next_page(view_state, dep, session, request_timeout=30):
    # OBTENER SIGUIENTE PÁGINA
    payload = goto_next_page_payload(view_state, dep)
    content = goto_page(payload, session, request_timeout=request_timeout)
    data, _ = data_souper(content)
    return data

def go_last_page(view_state, dep, session, request_timeout=30):
    # OBTENER ÚLTIMA PÁGINA
    payload = goto_last_page_payload(view_state, dep)
    content = goto_page(payload, session, request_timeout=request_timeout)
    data, _ = data_souper(content)
    return data

def go_prev_page(view_state, dep, session, request_timeout=30):
    # OBTENER PÁGINA PREVIA
    payload = goto_prev_page_payload(view_state, dep)
    content = goto_page(payload, session, request_timeout=request_timeout)
    data, _ = data_souper(content)
    return data

def left_to_rigth(view_state, dep, session, right=False, request_timeout=30):
    # SCRAPING IZQUIERDA A DERECHA
    data, total_pages = go_first_page(view_state, dep, session, request_timeout=request_timeout)
    data_list = [data]

    if not total_pages or total_pages <= 1:
            return pd.concat(data_list, ignore_index=True)    
    
    for _ in tqdm(range(total_pages - 1), desc=f"Scraping Dep {dep}"):
        try:
            # Simula lectura humana
            time.sleep(random.uniform(1.5, 3.0))
            data = go_next_page(view_state, dep, session, request_timeout=request_timeout)
            data_list.append(data)
        except Exception:
            break
    return pd.concat(data_list, ignore_index=True)

def right_to_left(view_state, dep, session, left=True, request_timeout=30):
    # SCRAPING DERECHA A IZQUIERDA
    _, total_pages = go_first_page(view_state, dep, session, request_timeout=request_timeout)
    data = go_last_page(view_state, dep, session, request_timeout=request_timeout)
    data_list = [data]

    if not total_pages or total_pages <= 1:
        return pd.concat(data_list, ignore_index=True)

    # for _ in tqdm(range(limite - 1)):
    for _ in tqdm(range(total_pages - 1), desc=f"Scraping Inverso Dep {dep}"):
        try:
            time.sleep(random.uniform(1.5, 3.0))
            data = go_prev_page(view_state, dep, session, request_timeout=request_timeout)
            data_list.append(data)
        except Exception:
            break

    return pd.concat(data_list, ignore_index=True)
