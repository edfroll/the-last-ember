# Runs on world load / reload.
scoreboard objectives add le.init dummy
scoreboard players set #loaded le.init 1
# T-001b: no wandering traders
gamerule spawn_wandering_traders false
# T-001b: metal-gear drop control for natural mobs
schedule function last_ember:mob_eq/scan 10t replace
# T-004: global protection rules (see docs/reports/T-004-report.md for side effects)
gamerule mob_griefing false
gamerule fire_spread_radius_around_player 0
gamerule projectiles_can_break_blocks false
# T-004: adventure zones
scoreboard objectives add le.z dummy
scoreboard players set #5 le.z 5
scoreboard players set #20 le.z 20
function last_ember:zones/setup
# T-005: bonfires and the Ember
function last_ember:bonfire/setup
# T-006: safe biomes sweep
schedule function last_ember:biomes/safe_sweep 20t replace
# T-007: death, ash trails, urns
function last_ember:death/setup
function last_ember:refuge/gen/markers
# T-009: races, classes, Hall of Awakening
function last_ember:char/setup
# T-013: altars of the chapters, keys, properties of the Ember
function last_ember:altar/setup
# T-014: elite mobs
function last_ember:elite/setup
# T-015: insomnia, hallucinations, sleep
function last_ember:halluc/setup
# T-016: traps
function last_ember:trap/setup
# T-016: statues
function last_ember:statue/setup
# T-017: traders
function last_ember:trader/setup
# T-018: the monster lab, wounds
function last_ember:lab/setup
# T-019: treasuries (the layout of the main items at the first start)
function last_ember:vault/setup
# T-020: contracts on monsters
function last_ember:contract/setup
# T-021: region borders, chapter gates, shortcuts
function last_ember:gate/setup
