# CONFIGURACIÓN DE API Y PARÁMETROS
BASE_URL = "https://www.bumeran.com.pe/api/avisos/searchV2"

HEADERS = {
    "accept": "application/json",
    "accept-language": "es-419,es;q=0.9,es-ES;q=0.8,en;q=0.7,en-GB;q=0.6,en-US;q=0.5,es-MX;q=0.4,es-PE;q=0.3",
    "content-type": "application/json",
    "origin": "https://www.bumeran.com.pe",
    "priority": "u=1, i",
    "referer": "https://www.bumeran.com.pe/empleos.html",
    "sec-ch-ua": "\"Microsoft Edge\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "x-site-id": "BMPE",
}

# DATA BODY PARA FILTRO
DATA_BODY = {
    "filtros": [{"id": "nivel_laboral", "value": "junior"}]
}

PAGE_SIZE = 20

# CAMPOS A EXTRAER
CAMPOS = [
    'id',
    'titulo',
    'detalle',
    'aptoDiscapacitado',
    'idEmpresa',
    'empresa',
    'fechaHoraPublicacion',
    'fechaPublicacion',
    'fechaModificado',
    'localizacion',
    'tipoTrabajo',
    'modalidadTrabajo',
    'cantidadVacantes',
    'portal'
]