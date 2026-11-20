#!/bin/bash
# The Last Ember: setup script облачного окружения last-ember-mc26 (копия поля Setup script).
# Java 25, сервер 26.3, данные генератора, EULA (согласие Edward дано). Повторный запуск ничего не перекачивает.
set -eu
# репозиторий не подключён к сессии (нет GitHub-коннектора) — клонируем сами (репо публичный)
ls -d /home/user/*/datapack >/dev/null 2>&1 || git clone -q https://github.com/edfroll/the-last-ember /home/user/the-last-ember
R=$(dirname "$(ls -d /home/user/*/datapack | head -1)")
cd "$R" && mkdir -p server/jdk25
# rsync — для tools/server.sh setup/sync; vorbis-tools — oggenc; xvfb + libegl — клиенты Cam/Cam2
(apt-get update -q && apt-get install -y -q rsync zip vorbis-tools imagemagick xvfb libegl1 libegl-mesa0) >/dev/null 2>&1 || true
if ! ls server/jdk25/*/bin/java >/dev/null 2>&1; then
  curl -fsSL https://api.adoptium.net/v3/binary/latest/25/ga/linux/x64/jdk/hotspot/normal/eclipse -o /tmp/jdk25.tgz
  tar -xzf /tmp/jdk25.tgz -C server/jdk25
fi
if [ ! -f server/server-26.3.jar ]; then
  M=$(curl -fsSL https://piston-meta.mojang.com/mc/game/version_manifest_v2.json | python3 -c 'import json,sys;print([v["url"] for v in json.load(sys.stdin)["versions"] if v["id"]=="26.3"][0])')
  S=$(curl -fsSL "$M" | python3 -c 'import json,sys;print(json.load(sys.stdin)["downloads"]["server"]["url"])')
  curl -fsSL "$S" -o server/server-26.3.jar
fi
J="$(. tools/env.sh; le_java_home)/bin/java"
# генератор запускаем из server/: бандлер распаковывает libraries/ и versions/ в текущую папку
[ -d server/generated/reports ] || (cd server && "$J" -DbundlerMainClass=net.minecraft.data.Main -jar server-26.3.jar --reports --server --output generated)
echo eula=true > server/eula.txt
