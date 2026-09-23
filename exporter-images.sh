#!/bin/sh
# À lancer sur une machine AVEC Internet (ex. votre Mac) pour préparer
# une installation sur une machine SANS Internet (ex. Synology isolé).
# Produit slicer3d-images.tar, à importer ensuite avec :
#     docker load -i slicer3d-images.tar
set -e
ORCA=${ORCA_IMAGE:-lscr.io/linuxserver/orcaslicer:latest}
PROXY=${PROXY_IMAGE:-nginx:1.27-alpine}
docker pull --platform linux/amd64 "$ORCA"
docker pull --platform linux/amd64 "$PROXY"
docker save -o slicer3d-images.tar "$ORCA" "$PROXY"
echo "Images exportées dans slicer3d-images.tar"
