# Slicer 3D hors-ligne dans Docker (Artillery Sidewinder X2)

**OrcaSlicer** (interface graphique complète) dans Docker, utilisable depuis le
navigateur web, **sans aucun accès à Internet** pour le conteneur du slicer.
Fonctionne avec **Docker Desktop pour Mac** et **Synology (Container Manager)**.

```
 Navigateur ──► proxy (nginx) ──[réseau "isole", internal: true]──► orcaslicer
                  ports 3000/3001                                     aucune sortie
```

- `orcaslicer` n'est relié qu'au réseau `isole`, déclaré `internal: true` :
  Docker ne lui donne **aucune passerelle**. Il ne peut joindre ni Internet ni
  votre réseau local, et ne publie aucun port.
- `proxy` est un simple relais TCP nginx. C'est le seul conteneur joignable
  depuis votre navigateur.
- OrcaSlicer intègre le profil **Artillery Sidewinder X2** : le slicer n'a pas
  besoin d'Internet pour fonctionner.

## Contenu

| Fichier                 | Rôle                                                    |
|-------------------------|---------------------------------------------------------|
| `docker-compose.yml`    | Les 2 conteneurs et les 2 réseaux                       |
| `proxy/nginx.conf`      | Relais TCP vers le slicer                               |
| `.env.example`          | Réglages (IP d'écoute, ports, mot de passe, PUID/PGID)  |
| `verifier-isolation.sh` | Vérifie que le slicer n'a pas accès à Internet          |
| `exporter-images.sh`    | Prépare les images pour une machine sans Internet       |
| `projets/`              | Vos fichiers STL/3MF et G-code (visible sous `/projets`) |

> Seul l'hôte (Mac ou NAS) a besoin d'Internet, **une seule fois**, pour
> télécharger les images. Sinon, utilisez `exporter-images.sh` (voir plus bas).
> Les conteneurs eux-mêmes ne sortent jamais sur Internet.

---

## Installation sur Mac (Docker Desktop)

```sh
git clone <ce dépôt> slicer3d && cd slicer3d
cp .env.example .env          # les valeurs par défaut conviennent pour le Mac
docker compose up -d
```

Ouvrez ensuite **http://localhost:3000**.

- Par défaut l'accès est limité au Mac (`BIND_IP=127.0.0.1`).
- Sur un Mac Apple Silicon (M1/M2/M3/M4), l'image amd64 tourne via
  l'émulation. Dans Docker Desktop, activez *Settings → General → « Use
  Rosetta for x86_64/amd64 emulation on Apple Silicon »* pour de meilleures
  performances. Le découpage est un peu plus lent qu'en natif, mais tout
  fonctionne.

## Installation sur Synology (Container Manager, DSM 7.2+)

1. Dans **File Station**, créez `docker/slicer3d` et copiez-y tous les fichiers
   du dépôt. Créez aussi les dossiers vides `data/config` et `projets`.
2. Créez le fichier `.env` à partir de `.env.example` et modifiez :
   ```
   BIND_IP=0.0.0.0
   SLICER_USER=moi
   SLICER_PASSWORD=unMotDePasseSolide
   PUID=1026      # votre UID DSM (en SSH : id)
   PGID=100
   ```
3. **Container Manager → Projet → Créer**. Choisissez le chemin
   `docker/slicer3d` et « Utiliser le docker-compose.yml existant », puis
   lancez le projet.
4. Depuis un PC du réseau, ouvrez **https://IP-DU-NAS:3001**. Acceptez
   l'avertissement du certificat auto-signé.

> **Pourquoi HTTPS depuis une autre machine ?** Le bureau web a besoin d'un
> « contexte sécurisé » du navigateur. `http://localhost` en est un, mais
> `http://IP-du-NAS` n'en est pas un. Depuis le Mac, utilisez `:3000` ;
> depuis le LAN, utilisez `https://…:3001`.

Si le port 3000 ou 3001 est déjà pris sur le NAS, changez `HTTP_PORT` ou
`HTTPS_PORT` dans `.env`.

### NAS sans accès Internet du tout

Sur le Mac (avec Internet) :
```sh
./exporter-images.sh          # crée slicer3d-images.tar
```
Copiez `slicer3d-images.tar` sur le NAS, puis en SSH :
```sh
sudo docker load -i slicer3d-images.tar
```
Créez ensuite le projet comme ci-dessus. Aucun téléchargement ne sera tenté.

---

## Configurer l'Artillery Sidewinder X2

Au premier lancement, l'assistant d'OrcaSlicer s'ouvre :

1. **Région** : choisissez *Europe* (ou autre). Ignorez toute connexion à
   un compte ou à un « cloud ».
2. **Imprimantes** : dans la liste des fabricants, prenez **Artillery**, puis
   cochez **Artillery Sidewinder X2** (buse 0,4 mm).
3. **Filaments** : cochez ceux que vous utilisez (PLA, PETG…).
4. Si OrcaSlicer propose de télécharger le « Bambu Network Plugin » ou une
   mise à jour, refusez. Ce n'est pas nécessaire, et le téléchargement
   échouera de toute façon puisque le conteneur n'a pas Internet.

Relancer l'assistant plus tard : menu *Fichier → Assistant de configuration*.

## Utilisation au quotidien

- **Importer un modèle** : déposez vos fichiers dans le dossier `projets/` de
  l'hôte, puis dans OrcaSlicer ouvrez `/projets/...`. Vous pouvez aussi
  utiliser le panneau latéral du bureau web (icône de fichiers) pour envoyer
  ou télécharger des fichiers depuis le navigateur.
- **Exporter le G-code** : enregistrez-le dans `/projets`. Il apparaît aussitôt
  dans `projets/` sur le Mac ou le NAS. Copiez-le ensuite sur la carte SD de
  la X2.
- Vos profils et réglages sont conservés dans `data/config/`.

## Vérifier l'isolation

```sh
./verifier-isolation.sh
```
Le script lance `curl` vers Internet **depuis** le conteneur du slicer. Les
deux tests doivent échouer (« OK : Internet inaccessible »). Vous pouvez aussi
vérifier à la main :
```sh
docker network inspect slicer3d_isole --format '{{.Internal}}'   # doit afficher true
```

## Commandes utiles

```sh
docker compose logs -f orcaslicer   # journaux
docker compose restart              # redémarrer
docker compose down                 # arrêter
docker compose pull && docker compose up -d   # mettre à jour (hôte avec Internet)
```

## Sécurité (résumé)

- Le slicer n'a aucune route réseau vers l'extérieur (`internal: true`), ne
  publie aucun port et n'est joignable qu'à travers le proxy.
- Le proxy ne fait que relayer les connexions entrantes. Il tourne avec
  `no-new-privileges`, et sa configuration est montée en lecture seule.
- Sur le Mac, l'écoute est limitée à `127.0.0.1`. Sur le Synology, mettez un
  mot de passe (`SLICER_USER` / `SLICER_PASSWORD`) et n'ouvrez pas ces ports
  sur votre box.
