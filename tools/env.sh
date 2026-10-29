# Shared helpers for tools/*.sh (source it): the project JDK 25 in macOS or Linux layout, in-place sed, sha1.
_le_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
le_java_home() {  # server/jdk25/<jdk>/Contents/Home (macOS), server/jdk25 or server/jdk25/<jdk> (Linux)
  local d
  for d in "$_le_root"/server/jdk25/*/Contents/Home "$_le_root"/server/jdk25 "$_le_root"/server/jdk25/*; do
    [ -x "$d/bin/java" ] && { echo "$d"; return 0; }
  done
  echo "JDK 25 not found in server/jdk25" >&2; return 1
}
sedi() { if sed --version >/dev/null 2>&1; then sed -i "$@"; else sedi "$@"; fi; }  # GNU or BSD sed
sha1() { if command -v shasum >/dev/null; then shasum -a 1 "$1"; else sha1sum "$1"; fi | cut -d' ' -f1; }
