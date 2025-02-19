# CONFIG. GLOBAL
URL = "https://app.servir.gob.pe/DifusionOfertasExterno/faces/consultas/ofertas_laborales.xhtml"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive",
    "Host": "app.servir.gob.pe",
}

# PAYLOAD BASE COMPARTIDO
share_payload = {
    "javax.faces.partial.ajax": "true",
    "javax.faces.partial.execute": "@all",
    "javax.faces.partial.render": "frmLstOfertsLabo:mensaje frmLstOfertsLabo",
    "frmLstOfertsLabo": "frmLstOfertsLabo",
    "frmLstOfertsLabo:modalidadAcceso": "03",
    "frmLstOfertsLabo:txtPerfil": "",
    "frmLstOfertsLabo:cboDep_focus": "",
    "frmLstOfertsLabo:txtPuesto": "",
    "frmLstOfertsLabo:autocompletar_input": "",
    "frmLstOfertsLabo:autocompletar_hinput": "",
    "frmLstOfertsLabo:txtNroConv": "",
}

# PAYLOADS DE PÁGINA
first_page = {
    "javax.faces.source": "frmLstOfertsLabo:j_idt42",
    "frmLstOfertsLabo:j_idt42": "frmLstOfertsLabo:j_idt42",
}
next_page = {
    "javax.faces.source": "frmLstOfertsLabo:j_idt56",
    "frmLstOfertsLabo:j_idt56": "frmLstOfertsLabo:j_idt56",
}
last_page = {
    "javax.faces.source": "frmLstOfertsLabo:j_idt57",
    "frmLstOfertsLabo:j_idt57": "frmLstOfertsLabo:j_idt57",
}
prev_page = {
    "javax.faces.source": "frmLstOfertsLabo:j_idt54",
    "frmLstOfertsLabo:j_idt54": "frmLstOfertsLabo:j_idt54",
}
