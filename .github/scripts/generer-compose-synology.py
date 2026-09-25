#!/usr/bin/env python3
"""Génère le docker-compose.yml "tout-en-un" du paquet Synology.

Part de docker-compose.synology.yml et remplace les constructions d'images
(build:) des services "proxy" et "fichiers" par l'image nginx officielle, en
intégrant directement leurs fichiers (configs nginx, script, page web) dans
le compose. Résultat : UN SEUL fichier suffit sur le NAS, rien à construire,
aucun Dockerfile ni dossier à copier.

Utilisé uniquement par le workflow GitHub.
Usage : generer-compose-synology.py > docker-compose.yml
"""
import yaml

NGINX = "nginx:1.27-alpine"


def lire(chemin):
    # "$" -> "$$" : sinon docker compose tenterait d'y substituer des variables.
    return open(chemin, encoding="utf-8").read().replace("$", "$$")


class Bloc(str):
    """Chaîne multi-lignes, écrite en style bloc YAML (|) pour rester lisible."""


yaml.SafeDumper.add_representer(
    Bloc, lambda d, s: d.represent_scalar("tag:yaml.org,2002:str", s, style="|")
)

compose = yaml.safe_load(open("docker-compose.synology.yml", encoding="utf-8"))
svc = compose["services"]

# --- fichiers : page web + WebDAV, fichiers écrits au démarrage -------------
f = svc["fichiers"]
f.pop("build")
f["image"] = NGINX
f["environment"] = {
    "SLICER_USER": "${SLICER_USER:-}",
    "SLICER_PASSWORD": "${SLICER_PASSWORD:-}",
    "FICHIERS_NGINX_CONF": Bloc(lire("fichiers/nginx.conf")),
    "FICHIERS_START_SH": Bloc(lire("fichiers/start.sh")),
    "FICHIERS_INDEX_HTML": Bloc(lire("fichiers/www/index.html")),
}
f["entrypoint"] = [
    "/bin/sh", "-c",
    "mkdir -p /fichiers/www"
    ' && printf "%s" "$$FICHIERS_NGINX_CONF" > /fichiers/nginx.conf'
    ' && printf "%s" "$$FICHIERS_INDEX_HTML" > /fichiers/www/index.html'
    ' && printf "%s" "$$FICHIERS_START_SH" > /fichiers/start.sh'
    " && exec /bin/sh /fichiers/start.sh",
]

# --- proxy : config nginx écrite au démarrage --------------------------------
p = svc["proxy"]
p.pop("build")
p["image"] = NGINX
p["environment"] = {"PROXY_NGINX_CONF": Bloc(lire("proxy/nginx.conf"))}
p["entrypoint"] = [
    "/bin/sh", "-c",
    'printf "%s" "$$PROXY_NGINX_CONF" > /etc/nginx/nginx.conf'
    ' && exec nginx -g "daemon off;"',
]

# --- verification : l'image nginx contient wget ------------------------------
svc["verification"]["image"] = NGINX
svc["verification"].pop("pull_policy", None)

print("""\
# Slicer 3D (OrcaSlicer) pour Synology - fichier UNIQUE, rien d'autre à copier.
# Généré automatiquement depuis docker-compose.synology.yml (dépôt GitHub).
#
#   navigateur ──► [proxy] ──(réseau "isole", internal: true)──► [orcaslicer]
#                                                              └─► [fichiers]
#
# - Le NAS télécharge les images officielles ; les CONTENEURS restent sans
#   Internet (réseau "isole" sans passerelle) et sans accès aux dossiers du NAS.
# - Mot de passe : définissez SLICER_USER / SLICER_PASSWORD (fichier .env à
#   côté de ce fichier, ou remplacez les valeurs par défaut ci-dessous).
#   ATTENTION : dans ce fichier, un "$" doit être écrit "$$"
#   (mot de passe "$abc" -> écrire "$$abc"), sinon il est ignoré.
# - Slicer  : https://IP-DU-NAS:3001     Fichiers : http://IP-DU-NAS:3002
""")
print(yaml.safe_dump(compose, sort_keys=False, allow_unicode=True, width=1000))
