# as the marker of the shadow, at it; the viewer is @a[tag=le.hme]: if he turned to it, it is gone, else the figure is drawn for him only
tp @s ~ ~ ~ facing entity @a[tag=le.hme,limit=1]
execute store result score #my le.h run data get entity @s Rotation[0]
execute as @a[tag=le.hme,limit=1] store result score #py le.h run data get entity @s Rotation[0]
scoreboard players operation #d le.h = #my le.h
scoreboard players operation #d le.h -= #py le.h
scoreboard players add #d le.h 540
scoreboard players operation #d le.h %= #360 le.h
scoreboard players set #look le.h 0
execute if score #d le.h matches ..35 run scoreboard players set #look le.h 1
execute if score #d le.h matches 325.. run scoreboard players set #look le.h 1
execute if score #look le.h matches 1 as @a[tag=le.hme] run scoreboard players set @s le.hst 0
execute if score #look le.h matches 1 run return run kill @s
particle minecraft:dust{color:[0.0,0.0,0.0],scale:1.4} ~ ~0.35 ~ 0.14 0.3 0.14 0 4 force @a[tag=le.hme]
particle minecraft:dust{color:[0.0,0.0,0.0],scale:1.6} ~ ~0.95 ~ 0.2 0.35 0.12 0 5 force @a[tag=le.hme]
particle minecraft:dust{color:[0.0,0.0,0.0],scale:1.4} ~ ~1.55 ~ 0.14 0.2 0.12 0 4 force @a[tag=le.hme]
particle minecraft:dust{color:[0.0,0.0,0.0],scale:1.6} ~ ~1.9 ~ 0.1 0.1 0.1 0 3 force @a[tag=le.hme]
