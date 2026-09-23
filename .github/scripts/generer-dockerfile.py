#!/usr/bin/env python3
"""Génère un Dockerfile qui reconstruit une image, hors-ligne, à partir de
son système de fichiers exporté (rootfs.tar.gz), en reprenant sa config
(ENV, ENTRYPOINT, CMD, WORKDIR, USER, EXPOSE, VOLUME, STOPSIGNAL).

Utilisé uniquement par le workflow GitHub qui fabrique le zip hors-ligne.
Usage : generer-dockerfile.py <image> > Dockerfile
"""
import json
import subprocess
import sys

image = sys.argv[1]
cfg = json.loads(subprocess.check_output(["docker", "image", "inspect", image]))[0]["Config"]

lignes = [
    f"# Image reconstruite hors-ligne depuis : {image}",
    "FROM scratch",
    "ADD rootfs.tar.gz /",
]
for env in cfg.get("Env") or []:
    cle, _, val = env.partition("=")
    lignes.append(f"ENV {cle}={json.dumps(val, ensure_ascii=False).replace('$', chr(92) + '$')}")
if cfg.get("WorkingDir"):
    lignes.append(f"WORKDIR {cfg['WorkingDir']}")
if cfg.get("User"):
    lignes.append(f"USER {cfg['User']}")
for port in cfg.get("ExposedPorts") or {}:
    lignes.append(f"EXPOSE {port}")
if cfg.get("Volumes"):
    lignes.append(f"VOLUME {json.dumps(sorted(cfg['Volumes']))}")
if cfg.get("StopSignal"):
    lignes.append(f"STOPSIGNAL {cfg['StopSignal']}")
if cfg.get("Entrypoint"):
    lignes.append(f"ENTRYPOINT {json.dumps(cfg['Entrypoint'])}")
if cfg.get("Cmd"):
    lignes.append(f"CMD {json.dumps(cfg['Cmd'])}")

print("\n".join(lignes))
