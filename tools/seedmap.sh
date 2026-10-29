#!/usr/bin/env bash
# Headless seed maps. Usage: tools/seedmap.sh <outDir> <size> <stride> <seed> [seed...]
# Compiles tools/seedmap/SeedMap.java against the 26.3 server jar (cached in server/seedmap-build) and runs it.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; SRV="$ROOT/server"
. "$ROOT/tools/env.sh"; JAVA_HOME="$(le_java_home)"; export JAVA_HOME
B="$SRV/seedmap-build"; mkdir -p "$B"
INNER="$B/server-inner.jar"
[ -f "$INNER" ] || unzip -p "$SRV/server-26.3.jar" META-INF/versions/26.3/server-26.3.jar > "$INNER"
CP="$INNER:$(find "$SRV/libraries" -name '*.jar' | tr '\n' ':')"
if [ ! -f "$B/SeedMap.class" ] || [ "$ROOT/tools/seedmap/SeedMap.java" -nt "$B/SeedMap.class" ]; then
  "$JAVA_HOME/bin/javac" -cp "$CP" -d "$B" "$ROOT/tools/seedmap/SeedMap.java"
fi
exec "$JAVA_HOME/bin/java" -Xmx3G -cp "$B:$CP" SeedMap "$@"
