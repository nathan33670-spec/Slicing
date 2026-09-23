# Slicer 3D hors-ligne dans Docker (Artillery Sidewinder X2)

**OrcaSlicer** (interface graphique complète) dans Docker, utilisable depuis le
navigateur web, **sans aucun accès à Internet**. Fonctionne avec **Docker
Desktop pour Mac** et **Synology (Container Manager)**.

Deux paquets sont publiés dans les Releases GitHub :
- **`hors-ligne`**, pour le Mac sans Internet : tout est dans le zip.
- **`synology`**, pour le NAS avec Internet : les images sont téléchargées par
  le NAS.

**Tout repose sur `docker compose`**. Il n'y a aucun script `.sh` ou `.command`
à exécuter. Pour le Mac, rien n'est téléchargé.

```
 Navigateur ──► proxy (nginx) ──[réseau "isole", internal: true]──► orcaslicer
              ports 3000/3001/3002                              └──► fichiers
                                                                  aucune sortie
```

- `orcaslicer` et `fichiers` ne sont reliés qu'au réseau `isole`, déclaré
  `internal: true` : Docker ne leur donne **aucune passerelle**. Ils ne
  peuvent joindre ni Internet ni votre réseau local.
- `proxy` est un simple relais TCP nginx. C'est le seul conteneur joignable
  depuis votre navigateur.
- **Aucun dossier du Mac ou du NAS n'est monté dans les conteneurs.** Les
  fichiers entrent et sortent **uniquement par le navigateur**, grâce à la page
  « Fichiers » (port 3002). Ils sont stockés dans des volumes Docker internes.
- OrcaSlicer intègre le profil **Artillery Sidewinder X2**.

## Contenu du zip hors-ligne

| Élément                 | Rôle                                                       |
|-------------------------|------------------------------------------------------------|
| `docker-compose.yml`    | Les 3 conteneurs, les volumes et les 2 réseaux             |
| `.env`                  | Réglages (IP d'écoute, ports, mot de passe, PUID/PGID)     |
| `images/`               | Les images Docker, reconstruites localement par compose    |
| `proxy/`                | Configuration du relais                                    |
| `fichiers/`             | Page web d'envoi et de téléchargement de fichiers          |

Le dossier `images/` n'est pas dans le dépôt git, car il est trop volumineux.
Il est ajouté au zip par GitHub Actions (`.github/workflows/`). Chaque image y
est fournie sous forme de système de fichiers (`rootfs.tar.gz`) :
`docker compose` la reconstruit localement au premier lancement, sans aucun
accès réseau.

---

## Installation sur Mac (Docker Desktop)

1. Depuis une machine connectée, téléchargez `slicer3d-hors-ligne.zip` depuis
   la page **Releases → « hors-ligne »** du dépôt GitHub, puis copiez-le sur
   le Mac (clé USB…).
2. Décompressez-le (double-clic). Vous obtenez le dossier
   `slicer3d-hors-ligne`.
3. Lancez **Docker Desktop**. Si votre Mac est un Apple Silicon (M1 à M4),
   activez *Settings → General → « Use Rosetta for x86_64/amd64 emulation on
   Apple Silicon »*.
4. Ouvrez le **Terminal**, tapez `cd `, glissez le dossier
   `slicer3d-hors-ligne` dans la fenêtre, appuyez sur Entrée, puis lancez :
   ```sh
   docker compose up -d
   ```
   Le **premier** lancement reconstruit les images, ce qui prend quelques
   minutes. Les lancements suivants sont immédiats.
5. Ouvrez **http://localhost:3000** pour le slicer et
   **http://localhost:3002** pour les fichiers.

Par défaut, l'accès est limité au Mac lui-même (`BIND_IP=127.0.0.1`).

## Installation sur Synology (Container Manager, DSM 7.2+)

Le Synology a Internet : il utilise un **paquet dédié**, plus léger, qui
télécharge directement les images officielles. Les **conteneurs** restent
quand même sans Internet, grâce au même réseau isolé. Ce paquet est compatible
avec le moteur de construction de Container Manager.

1. Téléchargez `slicer3d-synology.zip` depuis la page
   **Releases → « synology »** du dépôt GitHub.
2. Dans **File Station**, créez le dossier `docker/slicer3d` et copiez-y le
   **contenu** du dossier `slicer3d-synology` : `docker-compose.yml`, `.env`,
   `proxy/`, `fichiers/`… Pour voir `.env` dans File Station, activez
   l'affichage des fichiers cachés.
3. Ouvrez `.env` avec l'éditeur de texte de DSM et définissez un mot de passe :
   ```
   SLICER_USER=moi
   SLICER_PASSWORD=unMotDePasseSolide
   ```
   Les autres valeurs sont déjà réglées pour un Synology (`BIND_IP=0.0.0.0`,
   `PUID=1026`, `PGID=100`).
4. **Container Manager → Projet → Créer**. Choisissez le chemin
   `docker/slicer3d` et « Utiliser le docker-compose.yml existant », puis
   lancez le projet. Le NAS télécharge les images, ce qui prend quelques
   minutes la première fois.
5. Depuis un PC du réseau, ouvrez **https://IP-DU-NAS:3001** pour le
   slicer. Acceptez l'avertissement du certificat auto-signé. Les fichiers
   sont sur **http://IP-DU-NAS:3002**.

Dans le dépôt git, ce paquet correspond à `docker-compose.synology.yml` (et
aux `Dockerfile` des dossiers `proxy/` et `fichiers/`).

> **Pourquoi HTTPS depuis une autre machine ?** Le bureau web a besoin d'un
> « contexte sécurisé » du navigateur. `http://localhost` en est un, mais
> `http://IP-du-NAS` n'en est pas un.

Si le port 3000, 3001 ou 3002 est déjà pris, changez `HTTP_PORT`,
`HTTPS_PORT` ou `FILES_PORT` dans `.env`.

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

Les fichiers passent **uniquement par le navigateur**, via la page
**Fichiers** (http://localhost:3002) :

1. **Envoyer un modèle** : sur la page Fichiers, glissez-déposez vos STL, 3MF
   ou OBJ, ou cliquez sur la zone pour les choisir.
2. **L'ouvrir dans OrcaSlicer** : *Fichier → Importer*, dossier **`/echange`**.
3. **Exporter le G-code** : enregistrez-le aussi dans **`/echange`**.
4. **Le récupérer** : sur la page Fichiers, cliquez sur *Actualiser* puis sur
   *Télécharger*. Copiez-le ensuite sur la carte SD de la X2.

La page permet aussi de créer des dossiers et de supprimer des fichiers.
Les profils, les réglages et le dossier `/echange` sont conservés dans des
volumes Docker internes : ils survivent aux redémarrages. Seul
`docker compose down -v` les efface.

## Vérifier l'isolation

```sh
docker compose run --rm verification
```
Un conteneur est lancé sur le réseau du slicer et tente de joindre Internet.
Tous les tests doivent afficher « OK », suivis de
`RÉSULTAT : isolé, aucun accès Internet.`

## Commandes utiles (depuis le dossier)

```sh
docker compose up -d                # démarrer
docker compose stop                 # arrêter
docker compose ps                   # état des conteneurs
docker compose logs -f orcaslicer   # journaux du slicer
docker compose down                 # supprimer les conteneurs (données conservées)
```

Sur Synology, les mêmes actions sont disponibles dans Container Manager →
Projet.

**Mettre à jour** : récupérez un nouveau zip, puis dans le nouveau dossier
lancez `docker compose build` et `docker compose up -d`. Les réglages et les
fichiers sont conservés.

## Sécurité (résumé)

- Le slicer et le service fichiers n'ont aucune route réseau vers l'extérieur
  (`internal: true`). Ils ne publient aucun port et ne sont joignables qu'à
  travers le proxy.
- Aucun dossier de l'hôte n'est monté dans les conteneurs : ils ne voient
  jamais le disque du Mac ou du NAS.
- Le proxy ne fait que relayer les connexions entrantes. Il tourne avec
  `no-new-privileges`.
- Sur le Mac, l'écoute est limitée à `127.0.0.1`. Sur le Synology, mettez un
  mot de passe (`SLICER_USER` / `SLICER_PASSWORD`, valable aussi pour la page
  Fichiers) et n'ouvrez pas ces ports sur votre box.
