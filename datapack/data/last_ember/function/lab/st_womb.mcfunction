function last_ember:lab/ground
function last_ember:lab/pool
fill ~-5 ~-1 ~-5 ~5 ~-1 ~5 minecraft:mud replace minecraft:grass_block
function last_ember:lab/label {t:"3 · Болотная утроба"}
scoreboard players set #dormant le.l 1
function last_ember:lab/womb/spawn
scoreboard players set #dormant le.l 0
