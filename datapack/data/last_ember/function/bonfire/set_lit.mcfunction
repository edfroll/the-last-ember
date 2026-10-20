# at the hearth (macro i): burning campfire with a hay bale under it (signal smoke), registry state = 1
setblock ~ ~-1 ~ minecraft:hay_block
setblock ~ ~ ~ minecraft:campfire[lit=true,signal_fire=true]
$data modify storage last_ember:bonfires by.b$(i).state set value 1
