particle minecraft:small_gust ~ ~ ~ 0.2 0.2 0.2 0 2 force @a[distance=..96]
particle minecraft:cloud ~ ~ ~ 0.1 0.1 0.1 0.01 1 force @a[distance=..96]
scoreboard players add #b le.cas 1
execute if score #b le.cas matches 64.. run return 0
execute if entity @s[distance=..2] run return 0
execute positioned ^ ^ ^1.5 run function last_ember:castle/beam_step
