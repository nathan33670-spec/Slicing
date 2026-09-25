#!/bin/bash
# Démarrage de Guacamole : génère le compte (user-mapping.xml) à partir de
# SLICER_USER / SLICER_PASSWORD, avec une seule connexion VNC vers le slicer,
# puis lance l'entrypoint officiel de l'image guacamole/guacamole.
set -e

xml() {  # échappe une valeur pour XML
    printf '%s' "$1" | sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g' -e 's/"/\&quot;/g'
}

UTILISATEUR=${SLICER_USER:-slicer}
MOT_DE_PASSE=${SLICER_PASSWORD:-slicer}

export GUACAMOLE_HOME=/tmp/modele-guacamole
mkdir -p "$GUACAMOLE_HOME"
cat > "$GUACAMOLE_HOME/user-mapping.xml" <<XML
<user-mapping>
  <authorize username="$(xml "$UTILISATEUR")" password="$(xml "$MOT_DE_PASSE")">
    <connection name="OrcaSlicer">
      <protocol>vnc</protocol>
      <param name="hostname">orcaslicer</param>
      <param name="port">5900</param>
      <param name="color-depth">24</param>
      <param name="cursor">remote</param>
    </connection>
  </authorize>
</user-mapping>
XML

exec /opt/guacamole/bin/entrypoint.sh
