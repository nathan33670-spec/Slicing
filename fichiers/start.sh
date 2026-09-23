#!/bin/sh
# Démarrage du service "fichiers" : prépare le dossier d'échange partagé
# avec le slicer, active le mot de passe si défini, puis lance nginx.
set -e

mkdir -p /echange
# Lecture/écriture pour le slicer (utilisateur abc) ET pour nginx.
chmod 0777 /echange

if [ -n "${SLICER_PASSWORD:-}" ]; then
    printf '%s:{PLAIN}%s\n' "${SLICER_USER:-slicer}" "$SLICER_PASSWORD" > /tmp/htpasswd
    chown root:nginx /tmp/htpasswd
    chmod 0640 /tmp/htpasswd
    printf 'auth_basic "Fichiers du slicer";\nauth_basic_user_file /tmp/htpasswd;\n' > /tmp/auth.conf
else
    : > /tmp/auth.conf
fi

# Fichiers/dossiers envoyés modifiables par le slicer (dav_access subit le umask).
umask 000
exec nginx -c /fichiers/nginx.conf -g 'daemon off;'
