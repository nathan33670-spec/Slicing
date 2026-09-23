#!/bin/sh
# Installation 100 % hors-ligne : charge les images fournies dans images/
# puis démarre le slicer. Aucun accès Internet n'est nécessaire.
set -e
cd "$(dirname "$0")"

if ! docker info >/dev/null 2>&1; then
    echo "Docker ne répond pas. Lancez Docker Desktop (ou Container Manager) puis réessayez."
    exit 1
fi

if ls images/*.tar >/dev/null 2>&1; then
    for f in images/*.tar; do
        echo "Chargement de l'image $f (cela peut prendre quelques minutes)..."
        docker load -i "$f"
    done
else
    echo "Aucune image dans images/ : on suppose qu'elles sont déjà chargées."
fi

[ -f .env ] || cp .env.example .env

docker compose up -d --pull never

. ./.env
echo
echo "Slicer démarré."
if [ "${BIND_IP:-127.0.0.1}" = "127.0.0.1" ]; then
    echo "Slicer   : http://localhost:${HTTP_PORT:-3000}"
    echo "Fichiers : http://localhost:${FILES_PORT:-3002}"
else
    echo "Depuis cette machine : http://localhost:${HTTP_PORT:-3000}"
    echo "Depuis le réseau     : https://<IP-de-cette-machine>:${HTTPS_PORT:-3001}"
    echo "Fichiers             : http://<IP-de-cette-machine>:${FILES_PORT:-3002}"
fi
