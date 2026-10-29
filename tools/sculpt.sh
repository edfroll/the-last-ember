#!/usr/bin/env bash
# Heightmap sculptor (T-003). Usage: tools/sculpt.sh apply|verify <spec.json> [profiles.csv]   (server must be STOPPED; world = server/world)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; SRV="$ROOT/server"
. "$ROOT/tools/env.sh"; JAVA_HOME="$(le_java_home)"; export JAVA_HOME
B="$SRV/seedmap-build"; mkdir -p "$B"; INNER="$B/server-inner.jar"
[ -f "$INNER" ] || unzip -p "$SRV/server-26.3.jar" META-INF/versions/26.3/server-26.3.jar > "$INNER"
CP="$INNER:$(find "$SRV/libraries" -name '*.jar' | tr '\n' ':')"
if [ ! -f "$B/Sculpt.class" ] || [ "$ROOT/tools/seedmap/Sculpt.java" -nt "$B/Sculpt.class" ]; then
  "$JAVA_HOME/bin/javac" -cp "$CP" -d "$B" "$ROOT/tools/seedmap/Sculpt.java"
fi
cd "$ROOT"
MODE="$1"; SPEC="$2"; shift 2
exec "$JAVA_HOME/bin/java" -Xmx3G -cp "$B:$CP" Sculpt "$MODE" "$SRV/world" "$SPEC" "$@" 2>&1 | grep -v WARN | sed "s/^\[[^]]*\] \[[^]]*\]: \[STD[A-Z]*\]: //"
