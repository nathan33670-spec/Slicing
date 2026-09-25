#!/usr/bin/env python3
"""Génère le docker-compose.yml "tout-en-un" du paquet Synology.

Part du modèle docker-compose.synology.yml et intègre directement dans le
compose les fichiers des services guacamole et proxy (script de démarrage,
config nginx). Ils sont écrits dans les conteneurs au démarrage.
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

# --- proxy : config nginx (Guacamole en HTTP, sans websocket) -----------------
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
#   navigateur ──► [proxy] ──(réseau "isole", internal: true)──► [guacamole] ─► [guacd] ─VNC/SFTP─► [orcaslicer]
#
# - TOUT passe par Apache Guacamole, en HTTP simple, SANS AUCUN websocket
#   (passe les proxys d'entreprise) : affichage d'OrcaSlicer et fichiers.
# - Le NAS télécharge les images ; les CONTENEURS restent sans Internet
#   (réseau "isole" sans passerelle) et sans accès aux dossiers du NAS.
# - Identifiant / mot de passe : modifiez les 2 lignes "utilisateur" et
#   "mot_de_passe" juste en dessous (par défaut : slicer / slicer).
#   ATTENTION : un "$" doit être écrit "$$" (mot de passe "$abc" -> "$$abc").
# - Ouvrir : http://IP-DU-NAS:3003
# - Fichiers : glisser-déposer dans la fenêtre pour envoyer ; menu Guacamole
#   (Ctrl+Alt+Maj, sur Mac Ctrl+Cmd+Maj) > Appareils > dossier pour télécharger.
""")
texte = yaml.safe_dump(compose, sort_keys=False, allow_unicode=True, width=1000)

# Identifiant et mot de passe définis UNE seule fois, en haut du fichier
# (ancres YAML), puis réutilisés partout (*utilisateur, *mot_de_passe).
for variable, ancre in (("SLICER_USER", "utilisateur"), ("SLICER_PASSWORD", "mot_de_passe")):
    for forme in (f"'${{{variable}:-}}'", f"${{{variable}:-}}"):
        texte = texte.replace(": " + forme + "\n", f": *{ancre}\n")
    assert f"${{{variable}:-}}" not in texte, variable
identifiants = """\
# ▼▼▼ À PERSONNALISER : identifiant et mot de passe (un "$" s'écrit "$$") ▼▼▼
x-identifiants:
  utilisateur: &utilisateur slicer
  mot_de_passe: &mot_de_passe slicer
# ▲▲▲ ─────────────────────────────────────────────────────────────────── ▲▲▲

"""
texte = texte.replace("services:\n", identifiants + "services:\n", 1)
print(texte)
