#!/usr/bin/env bash
# Local test server control. Usage: tools/server.sh {setup|start|stop|rcon "<cmd>"}
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRV="$ROOT/server"
. "$ROOT/tools/env.sh"; JAVA_HOME="$(le_java_home)"; export JAVA_HOME
JAVA="$JAVA_HOME/bin/java"
case "${1:-}" in
  setup|sync)  # copy datapack into the world, write config (EULA must already be accepted in server/eula.txt)
    mkdir -p "$SRV/world/datapacks"
    rsync -a --delete "$ROOT/datapack/" "$SRV/world/datapacks/last_ember/"  # symlinks are forbidden in worlds
    # the map's resource pack is pushed to every client by the server (served locally over HTTP on 127.0.0.1:8765)
    mkdir -p "$SRV/rp"; rm -f "$SRV/rp/last_ember.zip"; (cd "$ROOT/resourcepack" && zip -qrX "$SRV/rp/last_ember.zip" . -x '.*')
    SHA=$(sha1 "$SRV/rp/last_ember.zip")
    if [ -f "$SRV/server.properties" ]; then
      sedi -e "s#^resource-pack=.*#resource-pack=http://127.0.0.1:8765/last_ember.zip#" -e "s#^resource-pack-sha1=.*#resource-pack-sha1=$SHA#" \
        -e "s#^require-resource-pack=.*#require-resource-pack=true#" "$SRV/server.properties"
    fi
    [ -f "$SRV/server.properties" ] || cat > "$SRV/server.properties" <<P
enable-rcon=true
rcon.port=25575
rcon.password=ember-local-rcon
broadcast-rcon-to-ops=false
online-mode=false
view-distance=12
pause-when-empty-seconds=-1
white-list=false
simulation-distance=8
motd=The Last Ember (dev)
level-seed=
P
    ;;
  start)  "$0" sync
          pgrep -f "http.server 8765" >/dev/null || (nohup python3 -m http.server 8765 --bind 127.0.0.1 -d "$SRV/rp" > "$SRV/rp/http.log" 2>&1 &)
          cd "$SRV" && exec "$JAVA" -Xms2G -Xmx4G -jar server-26.3.jar nogui ;;
  stop)   python3 "$ROOT/tools/rcon.py" stop ;;
  rcon)   shift; python3 "$ROOT/tools/rcon.py" "$@" ;;
  *) echo "usage: $0 {setup|start|stop|rcon <cmd>}"; exit 1 ;;
esac
