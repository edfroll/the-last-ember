#!/usr/bin/env bash
# Seed scoring (T-002). Usage: tools/seedsearch.sh <out.csv> <stride> <from> <count> | <out.csv> <stride> list <s1,s2,...>
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; SRV="$ROOT/server"
export JAVA_HOME="$(ls -d "$SRV"/jdk25/*/Contents/Home)"
B="$SRV/seedmap-build"; mkdir -p "$B"; INNER="$B/server-inner.jar"
[ -f "$INNER" ] || unzip -p "$SRV/server-26.3.jar" META-INF/versions/26.3/server-26.3.jar > "$INNER"
CP="$INNER:$(find "$SRV/libraries" -name '*.jar' | tr '\n' ':')"
if [ ! -f "$B/SeedSearch.class" ] || [ "$ROOT/tools/seedmap/SeedSearch.java" -nt "$B/SeedSearch.class" ]; then
  "$JAVA_HOME/bin/javac" -cp "$CP" -d "$B" "$ROOT/tools/seedmap/SeedSearch.java"
fi
exec "$JAVA_HOME/bin/java" -Xmx3G -cp "$B:$CP" SeedSearch "$@"
