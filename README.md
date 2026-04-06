# Extract Empleos

Pipeline de scraping para reunir vacantes laborales y cargarlas en Supabase sin depender de archivos CSV como paso intermedio.

La idea del proyecto es simple: correr dos scrapers, normalizar sus resultados a un mismo esquema y hacer `upsert` directo en la tabla `jobs`. Con eso queda una base limpia para el matching posterior en NanoCV.

## Qué hace

- Ejecuta dos scrapers de empleo.
- Normaliza resultados de distintas fuentes a una sola estructura.
- Genera `job_uid` y `content_hash` para evitar duplicados.
- Hace `upsert` directo a Supabase.
- Está preparado para correr localmente o en un job programado.

## Estructura

```text
extract_empleos/
├── app/
│   ├── main.py
│   ├── normalizers.py
│   ├── pipeline.py
│   ├── settings.py
│   └── supabase_jobs.py
├── drivers/
├── scrapers/
│   ├── scraper_1/
│   └── scraper_2/
├── Dockerfile.scraper
├── requirements.txt
└── run_scrapers.sh
```

## Flujo actual

1. `run_scrapers.sh`
2. `python -m app.main`
3. Scraping
4. Normalización
5. `upsert` a Supabase

El flujo productivo ya no depende de guardar CSVs. Si más adelante se quiere agregar backup o auditoría, lo recomendable sería usar storage dedicado, no el filesystem del contenedor.

## Variables de entorno

El proyecto espera estas variables:

```env
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
RUN_SCRAPER_1=true
RUN_SCRAPER_2=true
PERSIST_LOCAL_OUTPUTS=false
UPSERT_CHUNK_SIZE=500
```

Puedes usar [`.env.example`](/Users/christianmagallanes/Repos/extract_empleos/.env.example) como base.

## Correr localmente

```bash
./run_scrapers.sh
```

## Probar con Docker

Construcción:

```bash
docker build -f Dockerfile.scraper -t extract-empleos:local .
```

Ejecución:

```bash
docker run --rm \
  --env-file .env \
  extract-empleos:local \
  /app/run_scrapers.sh
```

## Despliegue sugerido

La forma más cómoda de operar este repo es como un job programado:

- Railway cron
- o GitHub Actions schedule

La recomendación es elegir solo uno como scheduler principal para no duplicar corridas.

## Estado del proyecto

Versión actual: `v1.0.0`

Esta versión deja cerrada la base del pipeline de scraping:

- estructura más limpia
- ejecución por Docker
- integración directa con Supabase
- sin dependencia operativa de CSVs

