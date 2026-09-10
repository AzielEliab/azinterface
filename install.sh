#!/usr/bin/env bash
# AZInterface scripted install. Counted download via this project's Worker.
# Prefer: download the tarball, verify sha256, then extract + pip install -e .
# Advanced / optional (review this file first; do not pipe unread scripts):
#   curl -fsSL https://azinterface-download-tracker.vibelock.workers.dev/install.sh -o install-azinterface.sh
#   bash install-azinterface.sh
set -euo pipefail

HOST="${AZINTERFACE_HOST:-https://azinterface-download-tracker.vibelock.workers.dev}"
ASSET="${AZINTERFACE_ASSET:-azinterface-0.1.0.tar.gz}"
WORKDIR="${AZINTERFACE_HOME:-$HOME/azinterface}"

mkdir -p "$WORKDIR"
cd "$WORKDIR"

echo "Downloading counted tarball from ${HOST}/download (User-Agent Mozilla/5.0)…"
curl -fsSL -A 'Mozilla/5.0' "${HOST}/download?asset=${ASSET}" -o "${ASSET}"

tar -xzf "${ASSET}"
DIR="$(find . -maxdepth 1 -type d -name 'azinterface-*' | head -n 1)"
if [ -n "${DIR}" ]; then
  cd "${DIR}"
fi

python3 -m venv .venv
# shellcheck disable=SC1091
. .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .

echo
echo "Installed AZInterface."
echo "Run: azinterface ui"
echo "Then open http://127.0.0.1:8880 (loopback only)"
echo "Interface is CUSTODY — never Hub. Author: Aziel Eliab."
