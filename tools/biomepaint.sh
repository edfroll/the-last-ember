#!/usr/bin/env bash
# T-006 biome painter: tools/biomepaint.sh [paint.json]   (server STOPPED; world = server/world; default biomes/paint.gen.json)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; SRV="$ROOT/server"
export JAVA_HOME="$(ls -d "$SRV"/jdk25/*/Contents/Home)"
B="$SRV/seedmap-build"; mkdir -p "$B"; INNER="$B/server-inner.jar"
[ -f "$INNER" ] || unzip -p "$SRV/server-26.3.jar" META-INF/versions/26.3/server-26.3.jar > "$INNER"
CP="$INNER:$(find "$SRV/libraries" -name '*.jar' | tr '\n' ':')"
if [ ! -f "$B/BiomePaint.class" ] || [ "$ROOT/tools/seedmap/BiomePaint.java" -nt "$B/BiomePaint.class" ]; then
  "$JAVA_HOME/bin/javac" -cp "$CP" -d "$B" "$ROOT/tools/seedmap/BiomePaint.java"
fi
cd "$ROOT"
exec "$JAVA_HOME/bin/java" -Xmx3G -cp "$B:$CP" BiomePaint "$SRV/world" "${1:-biomes/paint.gen.json}" 2>&1 | grep -v WARN | sed "s/^\[[^]]*\] \[[^]]*\]: \[STD[A-Z]*\]: //"
