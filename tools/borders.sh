#!/usr/bin/env bash
# T-021 region borders (server STOPPED; world = server/world). Border lines: gates/borders.gen.json (python3 tools/gen_gates.py).
#   tools/borders.sh apply [id...]          barrier on the axis planes (every non-full block, y -64..319, outside the gaps); safe to repeat
#   tools/borders.sh holes <out> [id...]    passable cells left on the axes (outside the gaps)
#   tools/borders.sh wallmap x1 z1 x2 z2 <out>   columns closed from -64 to 319 (for tools/borders_check.py)
# Chunks that are not generated yet are skipped and listed.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; SRV="$ROOT/server"; WORLD="${LE_WORLD:-$SRV/world}"   # LE_WORLD=<dir>: another world copy
. "$ROOT/tools/env.sh"; JAVA_HOME="$(le_java_home)"; export JAVA_HOME
B="$SRV/seedmap-build"; mkdir -p "$B"; INNER="$B/server-inner.jar"
[ -f "$INNER" ] || unzip -p "$SRV/server-26.3.jar" META-INF/versions/26.3/server-26.3.jar > "$INNER"
CP="$INNER:$(find "$SRV/libraries" -name '*.jar' | tr '\n' ':')"
if [ ! -f "$B/Borders.class" ] || [ "$ROOT/tools/seedmap/Borders.java" -nt "$B/Borders.class" ] || [ "$ROOT/tools/seedmap/BlockWriter.java" -nt "$B/BlockWriter.class" ]; then
  "$JAVA_HOME/bin/javac" -cp "$CP" -d "$B" "$ROOT/tools/seedmap/BlockWriter.java" "$ROOT/tools/seedmap/Borders.java"
fi
cd "$ROOT"; MODE=$1; shift
case "$MODE" in
  apply) set -- apply "$WORLD" "$ROOT/gates/borders.gen.json" "$@";;
  holes) OUT=$1; shift; set -- holes "$WORLD" "$ROOT/gates/borders.gen.json" "$OUT" "$@";;
  wallmap) set -- wallmap "$WORLD" "$@";;
  *) echo "usage: $0 apply|holes|wallmap ..."; exit 1;;
esac
exec "$JAVA_HOME/bin/java" -Xmx3G -cp "$B:$CP" Borders "$@" 2>&1 | grep -v "WARN\|JAVA_TOOL_OPTIONS" | sed "s/^\[[^]]*\] \[[^]]*\]: \[STD[A-Z]*\]: //"
