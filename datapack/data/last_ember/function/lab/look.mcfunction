# le.llook 0..12: the head turned -60..60 degrees from the body toward the nearest player (6 = straight)
scoreboard players set @s le.llook 6
execute unless entity @a[distance=..16,gamemode=!spectator] run return 0
summon minecraft:marker ~ ~ ~ {Tags:["le.laim"]}
execute as @e[type=minecraft:marker,tag=le.laim,limit=1] at @s run tp @s ~ ~ ~ facing entity @p[distance=..16,gamemode=!spectator] eyes
execute store result score #fy le.l run data get entity @e[type=minecraft:marker,tag=le.laim,limit=1] Rotation[0]
kill @e[type=minecraft:marker,tag=le.laim]
execute store result score #by le.l run data get entity @s Rotation[0]
scoreboard players operation #fy le.l -= #by le.l
scoreboard players add #fy le.l 540
scoreboard players operation #fy le.l %= #360 le.l
scoreboard players remove #fy le.l 180
execute if score #fy le.l matches 61.. run scoreboard players set #fy le.l 60
execute if score #fy le.l matches ..-61 run scoreboard players set #fy le.l -60
scoreboard players add #fy le.l 65
scoreboard players operation #fy le.l /= #10 le.l
scoreboard players set @s le.llook 12
scoreboard players operation @s le.llook -= #fy le.l
