function last_ember:lab/ground
fill ~-5 ~-1 ~-5 ~5 ~-1 ~5 minecraft:coarse_dirt replace minecraft:grass_block
function last_ember:lab/label {t:"5 · Гигантская сколопендра"}
scoreboard players set #dormant le.l 1
function last_ember:lab/fish/spawn
scoreboard players set #dormant le.l 0
