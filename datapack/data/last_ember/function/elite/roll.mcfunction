# as a mob at itself, once (the scan of mob_eq): does it become an elite?
tag @s add le.rolled
execute unless entity @s[type=#last_ember:elite_types] run return 0
execute if entity @s[tag=le.boss] run return 0
execute if entity @s[tag=le.giant] run return 0
execute if entity @s[tag=le.npc] run return 0
execute if entity @s[tag=le.noelite] run return 0
execute if entity @s[tag=le.elite] run return 0
execute if entity @s[type=#last_ember:cube_mobs] run scoreboard players set #sz le.el 0
execute if entity @s[type=#last_ember:cube_mobs] store result score #sz le.el run data get entity @s Size
execute if entity @s[type=#last_ember:cube_mobs] if score #sz le.el matches ..2 run return 0
# the chance in 1/10000: surface 2 %, cave 6 %, dungeon zone 10 %; a faded region x1.5; night on the surface x1.25; at most 20 %
function last_ember:elite/gen/region
function last_ember:elite/gen/dungeon
scoreboard players set #ch le.el 200
scoreboard players set #sf le.el 1
execute unless predicate last_ember:can_see_sky run scoreboard players set #sf le.el 0
execute if score #sf le.el matches 0 run scoreboard players set #ch le.el 600
execute if score #dg le.el matches 1 run scoreboard players set #ch le.el 1000
execute if score #rg le.el matches 1..6 if score #chapters le.alt >= #rg le.el run scoreboard players operation #ch le.el *= #3 le.el
execute if score #rg le.el matches 1..6 if score #chapters le.alt >= #rg le.el run scoreboard players operation #ch le.el /= #2 le.el
execute if score #sf le.el matches 1 if score #dg le.el matches 0 if predicate last_ember:night run scoreboard players operation #ch le.el *= #5 le.el
execute if score #sf le.el matches 1 if score #dg le.el matches 0 if predicate last_ember:night run scoreboard players operation #ch le.el /= #4 le.el
execute if score #ch le.el matches 2001.. run scoreboard players set #ch le.el 2000
scoreboard players operation #ch le.el *= #elitechance le.el
scoreboard players operation #ch le.el /= #100 le.el
execute store result score #rl le.el run random value 0..9999
execute unless score #rl le.el < #ch le.el run return 0
function last_ember:elite/limits
execute if score #full le.el matches 1 run return 0
function last_ember:elite/make
