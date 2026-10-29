# as the monster (the attacking player has the tag le.catk): 1 when he stands in front of it (within 90 degrees of where it looks)
scoreboard players set #atk le.ct 0
execute unless entity @a[tag=le.catk] run return 0
scoreboard players set #atk le.ct 1
summon minecraft:marker ~ ~ ~ {Tags:["le.bmk3"]}
tp @e[type=minecraft:marker,tag=le.bmk3,limit=1] ~ ~ ~ facing entity @p[tag=le.catk] feet
execute store result score #my le.ct run data get entity @e[type=minecraft:marker,tag=le.bmk3,limit=1] Rotation[0]
execute store result score #py le.ct run data get entity @s Rotation[0]
kill @e[type=minecraft:marker,tag=le.bmk3]
scoreboard players operation #my le.ct -= #py le.ct
scoreboard players add #my le.ct 540
scoreboard players operation #my le.ct %= #360 le.ct
execute if score #my le.ct matches 90..270 run return 1
return 0
