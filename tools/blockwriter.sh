#!/usr/bin/env bash
# T-008 builder backend: tools/blockwriter.sh apply|nbt|heights ...   (see tools/seedmap/BlockWriter.java; world = server/world; server STOPPED for apply)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; SRV="$ROOT/server"
. "$ROOT/tools/env.sh"; JAVA_HOME="$(le_java_home)"; export JAVA_HOME
B="$SRV/seedmap-build"; INNER="$B/server-inner.jar"; CP="$INNER:$(find "$SRV/libraries" -name '*.jar' | tr '\n' ':')"
if [ ! -f "$B/BlockWriter.class" ] || [ "$ROOT/tools/seedmap/BlockWriter.java" -nt "$B/BlockWriter.class" ]; then "$JAVA_HOME/bin/javac" -cp "$CP" -d "$B" "$ROOT/tools/seedmap/BlockWriter.java"; fi
cd "$ROOT"; MODE=$1; shift
case "$MODE" in apply|heights) set -- "$MODE" "$SRV/world" "$@";; *) set -- "$MODE" "$@";; esac
exec "$JAVA_HOME/bin/java" -Xmx3G -cp "$B:$CP" BlockWriter "$@" 2>&1 | grep -v WARN | sed "s/^\[[^]]*\] \[[^]]*\]: \[STD[A-Z]*\]: //"
