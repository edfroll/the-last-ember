# as a cauldron interaction, at itself (the interaction stands at the foot of the cauldron block); scores: le.cmask (ingredients), le.cstate (1 = brewing),
# le.ctimer (calls of 4 ticks left), le.crec (recipe), le.ctier (tier of the healer), le.cbase (ticks the mushroom base has been in the water)
execute unless score @s le.cmask = @s le.cmask run function last_ember:potion/cauldron_init
execute if score @s le.cstate matches 1 run return run function last_ember:potion/brewing
tag @s add le.cur
execute positioned ~ ~0.45 ~ as @e[type=minecraft:item,distance=..0.9] at @s run function last_ember:potion/item_in
tag @s remove le.cur
scoreboard players operation #t le.e = @s le.cmask
scoreboard players operation #t le.e %= #2 le.e
execute if score #t le.e matches 1 run scoreboard players add @s le.cbase 4
execute if score #t le.e matches 0 run scoreboard players set @s le.cbase 0
execute if score @s le.cmask matches 1.. run function last_ember:potion/try_start
