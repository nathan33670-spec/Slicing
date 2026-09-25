# OrcaSlicer avec un serveur VNC (TigerVNC) et un serveur SFTP, pour être
# utilisé via Apache Guacamole en HTTP simple (sans websocket) : affichage
# par VNC, transfert de fichiers par SFTP (dossier /echange uniquement).
#
# Base : l'image linuxserver OrcaSlicer (OrcaSlicer + toutes ses dépendances,
# profils Artillery inclus). Son bureau web (Selkies, qui exige un websocket)
# n'est PAS lancé : on démarre à la place Xvnc + Openbox + OrcaSlicer + sshd.
FROM lscr.io/linuxserver/orcaslicer:latest

RUN apt-get update \
 && apt-get install -y --no-install-recommends tigervnc-standalone-server openssh-server \
 && rm -rf /var/lib/apt/lists/* \
 # Toutes les fenêtres s'ouvrent maximisées (plein écran dans le navigateur)
 && sed -i 's|<applications>|<applications><application class="*"><maximized>yes</maximized></application>|' \
        /etc/xdg/openbox/rc.xml \
 # SFTP uniquement (pas de shell), pour l'utilisateur "abc", dans /echange
 && printf '%s\n' \
      '' \
      '# --- Slicer 3D : SFTP seul, pour Guacamole ---' \
      'PermitRootLogin no' \
      'PasswordAuthentication yes' \
      'AllowUsers abc' \
      'Match User abc' \
      '    ForceCommand internal-sftp -u 000 -d /echange' \
      '    AllowTcpForwarding no' \
      '    X11Forwarding no' \
      '    PermitTTY no' \
      >> /etc/ssh/sshd_config

COPY demarrer.sh /usr/local/bin/demarrer-orcaslicer-vnc
RUN chmod 0755 /usr/local/bin/demarrer-orcaslicer-vnc

EXPOSE 5900 22
ENTRYPOINT ["/usr/local/bin/demarrer-orcaslicer-vnc"]
