#!/usr/bin/env bash
# Local test server control. Usage: tools/server.sh {setup|start|stop|rcon "<cmd>"}
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRV="$ROOT/server"
export JAVA_HOME="$(ls -d "$SRV"/jdk25/*/Contents/Home)"
JAVA="$JAVA_HOME/bin/java"
case "${1:-}" in
  setup|sync)  # copy datapack into the world, write config (EULA must already be accepted in server/eula.txt)
    mkdir -p "$SRV/world/datapacks"
    rsync -a --delete "$ROOT/datapack/" "$SRV/world/datapacks/last_ember/"  # symlinks are forbidden in worlds
    [ -f "$SRV/server.properties" ] || cat > "$SRV/server.properties" <<P
enable-rcon=true
rcon.port=25575
rcon.password=ember-local-rcon
broadcast-rcon-to-ops=false
online-mode=false
view-distance=12
pause-when-empty-seconds=-1
simulation-distance=8
motd=The Last Ember (dev)
level-seed=
P
    ;;
  start)  "$0" sync; cd "$SRV" && exec "$JAVA" -Xms2G -Xmx4G -jar server-26.3.jar nogui ;;
  stop)   python3 "$ROOT/tools/rcon.py" stop ;;
  rcon)   shift; python3 "$ROOT/tools/rcon.py" "$@" ;;
  *) echo "usage: $0 {setup|start|stop|rcon <cmd>}"; exit 1 ;;
esac
