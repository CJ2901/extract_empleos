#!/usr/bin/env bash

set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${BASE_DIR}/venv"
VENV_PYTHON="${VENV_DIR}/bin/python3"

if [ -x "/opt/homebrew/bin/python3" ]; then
  PYTHON_BIN="/opt/homebrew/bin/python3"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  echo "No se encontró python3 en el sistema."
  exit 1
fi

cd "${BASE_DIR}"

if [ ! -d "${VENV_DIR}" ]; then
  echo "Creando entorno virtual en ${VENV_DIR}"
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

source "${VENV_DIR}/bin/activate"
export PYTHONPATH="${BASE_DIR}:${PYTHONPATH:-}"

if [ -f "${BASE_DIR}/.env" ]; then
  set -a
  source "${BASE_DIR}/.env"
  set +a
fi

echo "Instalando dependencias"
"${VENV_PYTHON}" -m pip install --upgrade pip
"${VENV_PYTHON}" -m pip install -r requirements.txt

echo "Ejecutando scraping y subiendo directo a Supabase"
exec "${VENV_PYTHON}" -m app.main
