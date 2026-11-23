# T-031: the Village of Heather and the Dragon Ridge (R1), called from last_ember:load. Blocks: tools/build/r1_heather.py (offline);
# the generated part: function/heather/gen/* (tools/build/heather_dp.py, the scores explained there), dialogs dialog/heather/*, the
# templates structure/heather/head.nbt, sword_lo|hi.nbt, the zones `heather` (adventure, spawning on) and `heather_head`. No fading
# (the card: the village has nothing to fade; bonfire 9 fades by the common rule of T-023).
scoreboard objectives add le.hv dummy
scoreboard objectives add le.hn dummy
scoreboard objectives add le.hgen dummy
scoreboard objectives add le.hyaw dummy
scoreboard objectives add le.hoff dummy
scoreboard objectives add le.hrg dummy
scoreboard objectives add le.hmetg dummy
scoreboard objectives add le.htrig trigger
scoreboard objectives add le.hwin dummy
execute unless score #rgen le.hv = #rgen le.hv run scoreboard players set #rgen le.hv 0
execute unless score #met le.hv = #met le.hv run scoreboard players set #met le.hv 0
execute unless score #frz le.hv = #frz le.hv run scoreboard players set #frz le.hv 0
execute unless score #ms le.hv = #ms le.hv run scoreboard players set #ms le.hv 0
execute unless data storage last_ember:heather q run data modify storage last_ember:heather q set value 0
scoreboard players set #rmiss le.hv 0
scoreboard players set #2 le.hv 2
schedule function last_ember:heather/loop 5t replace
