#!/usr/bin/env bash
# T-022 terrain backend (server STOPPED; world = server/world or LE_WORLD). See tools/seedmap/Terrain.java.
#   tools/terrain.sh scan x1 z1 x2 z2 <out.bin>     ground/top/water per column
#   tools/terrain.sh apply <grid.bin>               rewrite the grid's columns (tools/build/r1.py writes the grid)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; SRV="$ROOT/server"; WORLD="${LE_WORLD:-$SRV/world}"
. "$ROOT/tools/env.sh"; JAVA_HOME="$(le_java_home)"; export JAVA_HOME
B="$SRV/seedmap-build"; mkdir -p "$B"; INNER="$B/server-inner.jar"
[ -f "$INNER" ] || unzip -p "$SRV/server-26.3.jar" META-INF/versions/26.3/server-26.3.jar > "$INNER"
CP="$INNER:$(find "$SRV/libraries" -name '*.jar' | tr '\n' ':')"
if [ ! -f "$B/Terrain.class" ] || [ "$ROOT/tools/seedmap/Terrain.java" -nt "$B/Terrain.class" ]; then
  "$JAVA_HOME/bin/javac" -cp "$CP" -d "$B" "$ROOT/tools/seedmap/Terrain.java"
fi
cd "$ROOT"; MODE=$1; shift
exec "$JAVA_HOME/bin/java" -Xmx6G -cp "$B:$CP" Terrain "$MODE" "$WORLD" "$@" 2>&1 | grep -v "WARN\|JAVA_TOOL_OPTIONS" | sed "s/^\[[^]]*\] \[[^]]*\]: \[STD[A-Z]*\]: //"
