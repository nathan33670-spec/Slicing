#!/bin/bash
# Lance Xvnc (écran virtuel + serveur VNC), Openbox et OrcaSlicer.
# Le port VNC (5900) n'est joignable que sur le réseau Docker isolé, par guacd.
set -e

PUID=${PUID:-1000}
PGID=${PGID:-1000}
RESOLUTION=${RESOLUTION:-1920x1080}

# Utilisateur "abc" aligné sur PUID/PGID (droits sur les volumes)
groupmod -o -g "$PGID" abc
usermod -o -u "$PUID" abc >/dev/null
mkdir -p /config/.config /echange
chown abc:abc /config /config/.config
chmod 0777 /echange
umask 000   # fichiers créés modifiables par le service "fichiers"

lancer() {  # exécute une commande en tant que "abc"
    runuser -u abc -- env HOME=/config DISPLAY=:1 LC_ALL=C \
        XDG_RUNTIME_DIR=/tmp/runtime-abc "$@"
}
mkdir -p /tmp/runtime-abc && chown abc:abc /tmp/runtime-abc && chmod 700 /tmp/runtime-abc
rm -f /tmp/.X1-lock /tmp/.X11-unix/X1

lancer Xvnc :1 -geometry "$RESOLUTION" -depth 24 -rfbport 5900 \
    -SecurityTypes None -localhost no -AlwaysShared -desktop OrcaSlicer &
for i in $(seq 1 50); do [ -e /tmp/.X11-unix/X1 ] && break; sleep 0.2; done

lancer dbus-launch --exit-with-session openbox &

# OrcaSlicer est relancé automatiquement s'il est fermé
while true; do
    lancer /opt/orcaslicer/AppRun || true
    sleep 2
done
