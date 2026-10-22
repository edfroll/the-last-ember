# Flame: the enemies around (radius 6 .. 12) burn for 5 s; fire blocks 5 s under them only in safe places (see fire_one)
scoreboard players operation #r le.e = @s le.tier
scoreboard players add #r le.e 6
execute store result storage last_ember:seer c.r int 1 run scoreboard players get #r le.e
function last_ember:seer/do_4_m with storage last_ember:seer c
particle minecraft:flame ~ ~1 ~ 1 0.6 1 0.05 60
playsound minecraft:item.firecharge.use player @a[distance=..20] ~ ~ ~ 1 0.7
return 1
