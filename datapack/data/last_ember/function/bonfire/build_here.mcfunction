# Blocks of one bonfire around the hearth (~ ~ ~). Placeholder look until the Architect's card: platform, hearth, stela, 3x3 respawn pad.
# NOTE: callers use "positioned <int> <int> <int>", which centres x/z (+0.5): entities are summoned at ~ ~ ~, blocks use ~ (floor).
fill ~-3 ~-1 ~-5 ~3 ~-1 ~3 minecraft:polished_deepslate
fill ~-3 ~ ~-5 ~3 ~4 ~3 minecraft:air
setblock ~ ~-1 ~ minecraft:cobbled_deepslate
setblock ~ ~ ~ minecraft:campfire[lit=false]
setblock ~2 ~ ~ minecraft:chiseled_deepslate
setblock ~2 ~1 ~ minecraft:polished_blackstone_wall
fill ~-1 ~-1 ~-4 ~1 ~-1 ~-2 minecraft:stone_bricks
kill @e[type=minecraft:interaction,tag=le.bonfire,distance=..3.5]
summon minecraft:interaction ~ ~ ~ {width:1.05f,height:1.0f,response:1b,Tags:["le.bonfire","le.hearth","le.new"]}
summon minecraft:interaction ~2 ~ ~ {width:1.05f,height:2.0f,response:1b,Tags:["le.bonfire","le.stela","le.new"]}
execute as @e[type=minecraft:interaction,tag=le.new,distance=..4] run scoreboard players operation @s le.bidx = #i le.e
tag @e[type=minecraft:interaction,tag=le.new,distance=..4] remove le.new
