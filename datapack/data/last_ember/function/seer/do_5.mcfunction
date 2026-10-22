# Lift: the enemies around (radius 6 .. 12) fly up 6 .. 12 blocks and fall (vanilla fall damage); bosses and giants stay on the ground
scoreboard players operation #r le.e = @s le.tier
scoreboard players add #r le.e 6
execute store result storage last_ember:seer c.r int 1 run scoreboard players get #r le.e
function last_ember:seer/gen/lift_speed
function last_ember:seer/do_5_m with storage last_ember:seer c
particle minecraft:cloud ~ ~0.2 ~ 1 0.1 1 0.1 50
playsound minecraft:entity.breeze.jump player @a[distance=..20] ~ ~ ~ 1 0.8
return 1
