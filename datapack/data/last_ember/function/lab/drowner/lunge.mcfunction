# a leap at the nearest player: 0.85 block per tick along the ground, 0.38 up
execute store result score @s le.lfd run random value 100..160
execute if score #r le.l matches 0..1 run playsound last_ember:creature.alghoul.agressive_snarl hostile @a ~ ~ ~ 1.8 1
execute if score #r le.l matches 2 run playsound last_ember:creature.drowner.vo_attack hostile @a ~ ~ ~ 1.8 1
playsound last_ember:creature.drowner.swoosh hostile @a ~ ~1 ~ 1.0 0.8
particle minecraft:splash ~ ~0.8 ~ 0.3 0.4 0.3 0 12
execute facing entity @p[gamemode=!spectator,gamemode=!creative] feet positioned 0.0 0.0 0.0 rotated ~ 0 positioned ^ ^ ^0.85 run summon minecraft:marker ~ ~ ~ {Tags:["le.lvec"]}
data modify entity @s Motion set from entity @e[type=minecraft:marker,tag=le.lvec,limit=1] Pos
data modify entity @s Motion[1] set value 0.38d
kill @e[type=minecraft:marker,tag=le.lvec]
