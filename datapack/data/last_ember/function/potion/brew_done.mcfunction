# as the cauldron: the brew is ready
execute if score @s le.crec matches 1..99 run function last_ember:potion/emit_n
execute if score @s le.crec matches 101.. run function last_ember:potion/mod_done
function last_ember:potion/returns
execute if block ~ ~ ~ minecraft:water_cauldron[level=1] run setblock ~ ~ ~ minecraft:cauldron
execute if block ~ ~ ~ minecraft:water_cauldron[level=2] run setblock ~ ~ ~ minecraft:water_cauldron[level=1]
execute if block ~ ~ ~ minecraft:water_cauldron[level=3] run setblock ~ ~ ~ minecraft:water_cauldron[level=2]
scoreboard players set @s le.cmask 0
scoreboard players set @s le.cstate 0
scoreboard players set @s le.cbase 0
scoreboard players set @s le.crec 0
particle minecraft:happy_villager ~ ~1 ~ 0.3 0.3 0.3 0.1 12
playsound minecraft:entity.player.levelup block @a[distance=..12] ~ ~ ~ 0.5 1.6
