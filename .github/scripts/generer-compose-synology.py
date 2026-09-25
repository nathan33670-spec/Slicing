#!/usr/bin/env python3
"""Génère le docker-compose.yml "tout-en-un" du paquet Synology.

Part du modèle docker-compose.synology.yml et intègre directement dans le
compose les fichiers des services guacamole, fichiers et proxy (scripts,
configs nginx, page web). Ils sont écrits dans les conteneurs au démarrage.
Résultat : UN SEUL fichier suffit sur le NAS, rien à construire.

Utilisé uniquement par le workflow GitHub.
Usage : generer-compose-synology.py > docker-compose.yml
"""
import yaml


def lire(chemin):
    # "$" -> "$$" : sinon docker compose tenterait d'y substituer des variables.
    return open(chemin, encoding="utf-8").read().replace("$", "$$")


class Bloc(str):
    """Chaîne multi-lignes, écrite en style bloc YAML (|) pour rester lisible."""


yaml.SafeDumper.add_representer(
    Bloc, lambda d, s: d.represent_scalar("tag:yaml.org,2002:str", s, style="|")
)


def ecrire(variable, destination):
    """Commande shell qui écrit le contenu d'une variable dans un fichier."""
    return f'printf "%s" "$${variable}" > {destination}'


compose = yaml.safe_load(open("docker-compose.synology.yml", encoding="utf-8"))
svc = compose["services"]

# --- guacamole : génération du compte puis démarrage officiel ---------------
g = svc["guacamole"]
g["environment"]["GUACAMOLE_START_SH"] = Bloc(lire("guacamole/start.sh"))
g["entrypoint"] = [
    "/bin/bash", "-c",
    ecrire("GUACAMOLE_START_SH", "/tmp/demarrer-guacamole.sh")
    + " && exec /bin/bash /tmp/demarrer-guacamole.sh",
]

# --- fichiers : page web + WebDAV --------------------------------------------
f = svc["fichiers"]
f["environment"].update({
    "FICHIERS_NGINX_CONF": Bloc(lire("fichiers/nginx.conf")),
    "FICHIERS_START_SH": Bloc(lire("fichiers/start.sh")),
    "FICHIERS_INDEX_HTML": Bloc(lire("fichiers/www/index.html")),
})
f["entrypoint"] = [
    "/bin/sh", "-c",
    "mkdir -p /fichiers/www"
    " && " + ecrire("FICHIERS_NGINX_CONF", "/fichiers/nginx.conf")
    + " && " + ecrire("FICHIERS_INDEX_HTML", "/fichiers/www/index.html")
    + " && " + ecrire("FICHIERS_START_SH", "/fichiers/start.sh")
    + " && exec /bin/sh /fichiers/start.sh",
]

# --- proxy : config nginx (Guacamole en HTTP, websocket bloqué) ---------------
p = svc["proxy"]
p["environment"] = {"PROXY_NGINX_CONF": Bloc(lire("proxy/nginx-guacamole.conf"))}
p["entrypoint"] = [
    "/bin/sh", "-c",
    ecrire("PROXY_NGINX_CONF", "/etc/nginx/nginx.conf")
    + ' && exec nginx -g "daemon off;"',
]

print("""\
# Slicer 3D (OrcaSlicer) pour Synology - fichier UNIQUE, rien d'autre à copier.
# Généré automatiquement depuis docker-compose.synology.yml (dépôt GitHub).
#
#   navigateur ──► [proxy] ──(réseau "isole", internal: true)──► [guacamole] ─► [guacd] ─VNC─► [orcaslicer]
#                                                             └──► [fichiers]
#
# - Affichage via Apache Guacamole en HTTP simple (sans websocket) : passe
#   les proxys d'entreprise.
# - Le NAS télécharge les images ; les CONTENEURS restent sans Internet
#   (réseau "isole" sans passerelle) et sans accès aux dossiers du NAS.
# - Identifiant / mot de passe : définissez SLICER_USER / SLICER_PASSWORD
#   (fichier .env à côté de ce fichier, ou remplacez les valeurs ci-dessous,
#   deux fois chacun). Sans valeur : slicer / slicer.
#   ATTENTION : dans ce fichier, un "$" doit être écrit "$$"
#   (mot de passe "$abc" -> écrire "$$abc"), sinon il est ignoré.
# - Slicer : http://IP-DU-NAS:3000     Fichiers : http://IP-DU-NAS:3002
""")
print(yaml.safe_dump(compose, sort_keys=False, allow_unicode=True, width=1000))
