function last_ember:lab/ground
fill ~-2 ~ ~-2 ~2 ~ ~2 minecraft:oak_leaves[persistent=true]
fill ~-1 ~ ~-1 ~1 ~ ~1 minecraft:air
fill ~-3 ~ ~-1 ~-3 ~1 ~1 minecraft:oak_leaves[persistent=true]
fill ~3 ~ ~-1 ~3 ~1 ~1 minecraft:oak_leaves[persistent=true]
function last_ember:lab/label {t:"2 · Варг"}
scoreboard players set #dormant le.l 1
function last_ember:lab/warg/spawn
scoreboard players set #dormant le.l 0
