# at an enemy: a fire block here only on air over a non-flammable full block, 2 blocks from anything that burns, outside the zones
execute unless block ~ ~ ~ minecraft:air run return 0
execute unless block ~ ~-1 ~ #last_ember:fire_floor run return 0
function last_ember:seer/gen/fire_near
execute if score #nf le.e matches 1 run return 0
summon marker ~ ~ ~ {Tags:["le.sfire","le.new"]}
execute as @e[type=marker,tag=le.new,distance=..0.1,limit=1] run function last_ember:seer/fire_mark
