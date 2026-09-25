# OrcaSlicer avec un serveur VNC (TigerVNC), pour être affiché via Apache
# Guacamole : Guacamole sait passer par de simples requêtes HTTP quand un
# proxy d'entreprise bloque les websockets.
#
# Base : l'image linuxserver OrcaSlicer (OrcaSlicer + toutes ses dépendances,
# profils Artillery inclus). On n'utilise pas son bureau web (Selkies) : on
# lance à la place Xvnc + Openbox + OrcaSlicer.
FROM lscr.io/linuxserver/orcaslicer:latest

RUN apt-get update \
 && apt-get install -y --no-install-recommends tigervnc-standalone-server \
 && rm -rf /var/lib/apt/lists/* \
 # Toutes les fenêtres s'ouvrent maximisées (plein écran dans le navigateur)
 && sed -i 's|<applications>|<applications><application class="*"><maximized>yes</maximized></application>|' \
        /etc/xdg/openbox/rc.xml

COPY demarrer.sh /usr/local/bin/demarrer-orcaslicer-vnc
RUN chmod 0755 /usr/local/bin/demarrer-orcaslicer-vnc

EXPOSE 5900
ENTRYPOINT ["/usr/local/bin/demarrer-orcaslicer-vnc"]
