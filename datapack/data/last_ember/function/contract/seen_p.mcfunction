summon minecraft:marker ~ ~ ~ {Tags:["le.bmk2"]}
tp @e[type=minecraft:marker,tag=le.bmk2,limit=1] ~ ~ ~ facing entity @e[type=minecraft:marker,tag=le.cpt,limit=1] feet
execute store result score #my le.ct run data get entity @e[type=minecraft:marker,tag=le.bmk2,limit=1] Rotation[0]
execute store result score #py le.ct run data get entity @s Rotation[0]
kill @e[type=minecraft:marker,tag=le.bmk2]
scoreboard players operation #my le.ct -= #py le.ct
scoreboard players add #my le.ct 540
scoreboard players operation #my le.ct %= #360 le.ct
execute if score #my le.ct matches 120..240 run scoreboard players set #seen le.ct 1
