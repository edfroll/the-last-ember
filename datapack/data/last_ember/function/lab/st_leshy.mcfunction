function last_ember:lab/ground
fill ~-5 ~-1 ~-5 ~5 ~-1 ~5 minecraft:moss_block replace minecraft:grass_block
setblock ~3 ~ ~3 minecraft:oak_log
setblock ~-4 ~ ~2 minecraft:oak_log
setblock ~-3 ~ ~-4 minecraft:oak_log
function last_ember:lab/label {t:"4 · Леший"}
scoreboard players set #dormant le.l 1
function last_ember:lab/leshy/spawn
scoreboard players set #dormant le.l 0
