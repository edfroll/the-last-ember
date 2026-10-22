# macro id, as a player at himself: #bh = 1 when the statue is more than 120 degrees away from the direction he looks
scoreboard players set #bh le.st 0
summon minecraft:marker ~ ~ ~ {Tags:["le.bmk"]}
$tp @e[type=minecraft:marker,tag=le.bmk,limit=1] ~ ~ ~ facing entity @e[tag=le.st_$(id),limit=1] feet
execute as @e[type=minecraft:marker,tag=le.bmk,limit=1] store result score #my le.st run data get entity @s Rotation[0]
execute store result score #py le.st run data get entity @s Rotation[0]
kill @e[type=minecraft:marker,tag=le.bmk]
scoreboard players operation #d le.st = #my le.st
scoreboard players operation #d le.st -= #py le.st
scoreboard players add #d le.st 540
scoreboard players set #360 le.st 360
scoreboard players operation #d le.st %= #360 le.st
execute if score #d le.st matches ..59 run scoreboard players set #bh le.st 1
execute if score #d le.st matches 301.. run scoreboard players set #bh le.st 1
