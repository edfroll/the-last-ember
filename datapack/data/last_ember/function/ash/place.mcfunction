# lava at the death spot -> urn; otherwise the nearest safe spot within 8 blocks, else urn
scoreboard players set #done le.e 0
$execute in $(dim) positioned $(x) $(y) $(z) if block ~ ~ ~ minecraft:lava run scoreboard players set #void le.e 1
$execute in $(dim) positioned $(x) $(y) $(z) if block ~ ~1 ~ minecraft:lava run scoreboard players set #void le.e 1
$execute if score #void le.e matches 0 in $(dim) positioned $(x) $(y) $(z) run function last_ember:ash/gen/find_spot
execute if score #done le.e matches 0 run function last_ember:ash/rec_to_urn
