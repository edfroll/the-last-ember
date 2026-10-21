# cauldron on top of the campfire + an interaction over it (tag le.pot) to take it back
$execute in $(dim) positioned $(x) $(y) $(z) run setblock ~ ~1 ~ minecraft:cauldron
$execute in $(dim) positioned $(x) $(y) $(z) run summon minecraft:interaction ~ ~1 ~ {width:1.05f,height:1.0f,response:1b,Tags:["le.bonfire","le.pot","le.potnew"]}
$scoreboard players set #i le.e $(i)
execute as @e[type=minecraft:interaction,tag=le.potnew] run scoreboard players operation @s le.bidx = #i le.e
tag @e[type=minecraft:interaction,tag=le.potnew] remove le.potnew
