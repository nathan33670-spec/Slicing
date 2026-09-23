#!/bin/sh
# Vérifie que le conteneur du slicer ne peut PAS sortir sur Internet.
set -u
C=slicer3d-orcaslicer

echo "Test 1 : accès HTTPS vers Internet depuis $C ..."
if docker exec "$C" curl -s -m 8 -o /dev/null https://www.google.com; then
    echo "  ÉCHEC : le slicer a accès à Internet !"; exit 1
else
    echo "  OK : Internet inaccessible."
fi

echo "Test 2 : accès IP directe (1.1.1.1) depuis $C ..."
if docker exec "$C" curl -s -m 8 -o /dev/null http://1.1.1.1; then
    echo "  ÉCHEC : le slicer peut joindre une IP externe !"; exit 1
else
    echo "  OK : IP externe injoignable."
fi

echo "Test 3 : réseaux du conteneur :"
docker inspect -f '{{range $k, $v := .NetworkSettings.Networks}}  - {{$k}}{{"\n"}}{{end}}' "$C"
echo "Tout est bon : le slicer est isolé."
