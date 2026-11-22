#!/usr/bin/env bash
# Before every PR: run every generator without test files (in dependency order) and fail if the committed output differs.
# Order: files other generators read come first (zones of bonfires/gates/traders -> gen_zones -> gen_seer/gen_elites read zones;
# gen_seer writes the staff loot tables gen_loot points to; gen_biomes calls gen_sounds).
# Usage: tools/check_gen.sh   (needs server/generated from the data generator for gen_no_ore/gen_t001)
set -uo pipefail
cd "$(dirname "$0")/.."
state() { git status --porcelain; git diff | sha1sum; git ls-files -o --exclude-standard | xargs -r cat 2>/dev/null | sha1sum; }
before=$(state)
fail=0
run() { echo "== $*"; if ! "$@" > /tmp/check_gen.out 2>&1; then echo "FAILED: $*"; tail -5 /tmp/check_gen.out; fail=1; fi; }
run python3 tools/gen_no_ore.py
run python3 tools/gen_t001.py
run python3 tools/gen_bonfires.py
run python3 tools/gen_gates.py
run python3 tools/gen_traders.py
run python3 tools/gen_zones.py
run python3 tools/gen_biomes.py
run python3 tools/gen_sounds.py
run python3 tools/gen_char.py
run python3 tools/gen_seer.py
run python3 tools/gen_potion.py
run python3 tools/gen_death.py
run python3 tools/gen_altars.py
run python3 tools/gen_regions.py
run python3 tools/gen_elites.py
run python3 tools/gen_traps.py
run python3 tools/gen_statues.py
run python3 tools/gen_lab.py
run python3 tools/gen_loot.py
run python3 tools/gen_contracts.py
run python3 tools/build/gen_runtime.py
run python3 tools/make_castle_textures.py
run python3 tools/make_advisor_skin.py
after=$(state)
if [ "$before" != "$after" ]; then
  echo; echo "CHANGED by the generators (commit the regenerated output, or fix the generator):"
  git status --short | sed 's/^/  /'
  fail=1
fi
[ $fail = 0 ] && echo "OK: every generator's output is committed" || { echo "CHECK FAILED"; exit 1; }
