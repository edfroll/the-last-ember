function last_ember:lab/ground
fill ~-2 ~-5 ~-2 ~2 ~-1 ~2 minecraft:mud
fill ~-1 ~-1 ~-1 ~1 ~-1 ~1 minecraft:water
function last_ember:lab/label {t:"1 · Утопленник-трупоед"}
scoreboard players set #dormant le.l 1
execute positioned ~ ~-1 ~ run function last_ember:lab/drowner/spawn
scoreboard players set #dormant le.l 0
