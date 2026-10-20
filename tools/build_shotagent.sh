#!/usr/bin/env bash
# Builds server/shotagent.jar (dev-only screenshot agent for the local client) against the 26.3 client jar.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export JAVA_HOME="$(ls -d "$ROOT"/server/jdk25/*/Contents/Home)"
CP=$(python3 -I - <<'P'
import json,os
mc=os.path.expanduser("~/Library/Application Support/minecraft")
d=json.load(open(mc+"/versions/26.3/26.3.json"))
out=[mc+"/versions/26.3/26.3.jar"]
for l in d["libraries"]:
    a=l.get("downloads",{}).get("artifact")
    if a:
        p=mc+"/libraries/"+(a.get("path") or a["url"].split("://",1)[1].split("/",1)[1])
        if os.path.exists(p): out.append(p)
print(":".join(out))
P
)
B="$ROOT/server/shotagent"; rm -rf "$B"; mkdir -p "$B"
"$JAVA_HOME/bin/javac" -cp "$CP" -d "$B" "$ROOT/tools/shotagent/ShotAgent.java"
printf 'Premain-Class: ShotAgent\n' > "$B/MANIFEST.MF"
(cd "$B" && "$JAVA_HOME/bin/jar" cfm ../shotagent.jar MANIFEST.MF ShotAgent*.class)
echo built "$ROOT/server/shotagent.jar"
