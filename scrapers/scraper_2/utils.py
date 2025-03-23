# FUNCIONES DE SCRAPING Y AUXILIARES
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup as bsoup
import warnings
from bs4 import XMLParsedAsHTMLWarning
from tqdm import tqdm
from config import URL, HEADERS, share_payload, first_page, next_page, last_page, prev_page

from selenium import webdriver
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



def first_session(url=URL, head=HEADERS, retries=3):
    options = Options()
    options.add_argument("--headless")  # Ejecuta en modo headless
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f'--user-agent={head.get("User-Agent", "")}')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.presence_of_element_located((By.NAME, "javax.faces.ViewState")))
        view_state = element.get_attribute("value")
    except Exception as e:
        driver.quit()
        raise Exception(f"Error al obtener el ViewState con Selenium: {e}")
    
    # Transferir cookies de Selenium a una sesión de requests
    session = requests.Session()
    for cookie in driver.get_cookies():
        session.cookies.set(cookie["name"], cookie["value"])
    
    # Obtén el HTML renderizado y crea el soup
    html = driver.page_source
    soup = bsoup(html, features="lxml")
    driver.quit()
    
    return session, soup, view_state


# def first_session(url=URL, head=HEADERS, retries=3):
#     # INICIAR SESIÓN Y OBTENER VIEWSTATE
#     session = requests.Session()
#     for attempt in range(retries):
#         req = session.get(url, headers=head)
#         soup = bsoup(req.content, features="lxml")
#         try:
#             view_state = get_view_state(soup)
#             return session, soup, view_state
#         except ValueError as e:
#             print(f"Intento {attempt + 1} de {retries} fallido: {e}")
    raise Exception("No se pudo obtener el ViewState después de varios intentos.")


def goto_page(data, session):
    # PETICIÓN POST CON PAYLOAD
    return session.post(url=URL, headers=HEADERS, data=data).content

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

def go_first_page(view_state, dep, session):
    # OBTENER PRIMERA PÁGINA
    payload = goto_first_dep_page_payload(view_state, dep)
    content = goto_page(payload, session)
    data, _ = data_souper(content)
    return data

def go_next_page(view_state, dep, session):
    # OBTENER SIGUIENTE PÁGINA
    payload = goto_next_page_payload(view_state, dep)
    content = goto_page(payload, session)
    data, _ = data_souper(content)
    return data

def go_last_page(view_state, dep, session):
    # OBTENER ÚLTIMA PÁGINA
    payload = goto_last_page_payload(view_state, dep)
    content = goto_page(payload, session)
    data, _ = data_souper(content)
    return data

def go_prev_page(view_state, dep, session):
    # OBTENER PÁGINA PREVIA
    payload = goto_prev_page_payload(view_state, dep)
    content = goto_page(payload, session)
    data, _ = data_souper(content)
    return data

def left_to_rigth(view_state, dep, session, right=False):
    # SCRAPING IZQUIERDA A DERECHA
    data = go_first_page(view_state, dep, session)
    data_list = [data]
    if right:
        # SI ES SCRAPING A DERECHA, LÍMITE FIJO (EJEMPLO)
        limite = 5
    else:
        limite = 5
    for _ in tqdm(range(limite - 1)):
        try:
            data = go_next_page(view_state, dep, session)
            data_list.append(data)
        except Exception:
            break
    return pd.concat(data_list, ignore_index=True)

def right_to_left(view_state, dep, session, left=True):
    # SCRAPING DERECHA A IZQUIERDA
    data = go_first_page(view_state, dep, session)
    data = go_last_page(view_state, dep, session)
    data_list = [data]
    limite = 5
    for _ in tqdm(range(limite - 1)):
        try:
            data = go_prev_page(view_state, dep, session)
            data_list.append(data)
        except Exception:
            break
    return pd.concat(data_list, ignore_index=True)
