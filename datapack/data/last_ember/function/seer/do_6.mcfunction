# Banish: in the cone ~90 degrees in front (reach 6 .. 9) the enemies fly off by that many blocks, the rest around (2 .. 3) by 2 .. 3; bosses and giants stay
tag @s add le.caster
scoreboard players operation #f le.e = @s le.tier
scoreboard players operation #f le.e /= #2 le.e
scoreboard players add #f le.e 6
scoreboard players operation #a le.e = @s le.tier
scoreboard players operation #a le.e /= #6 le.e
scoreboard players add #a le.e 2
execute store result score #cy le.e run data get entity @s Rotation[0]
execute store result storage last_ember:seer c.f int 1 run scoreboard players get #f le.e
execute store result storage last_ember:seer c.a int 1 run scoreboard players get #a le.e
kill @e[type=marker,tag=le.sp_m]
summon marker ~ ~ ~ {Tags:["le.sp_m"]}
function last_ember:seer/do_6_m with storage last_ember:seer c
kill @e[type=marker,tag=le.sp_m]
tag @s remove le.caster
particle minecraft:sweep_attack ^ ^1 ^1.5 0.8 0.3 0.8 0 6
particle minecraft:cloud ^ ^1 ^2 1.2 0.4 1.2 0.15 30
playsound minecraft:entity.breeze.wind_burst player @a[distance=..20] ~ ~ ~ 1 0.8
return 1
