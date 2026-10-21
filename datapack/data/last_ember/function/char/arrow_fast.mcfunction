# ranger: speed x1.5 (range x~2.0 with the air drag); the damage is divided back (so only the range changes) and multiplied by the tier (x1 .. x2)
execute store result entity @s Motion[0] double 0.0001 run data get entity @s Motion[0] 15000
execute store result entity @s Motion[1] double 0.0001 run data get entity @s Motion[1] 15000
execute store result entity @s Motion[2] double 0.0001 run data get entity @s Motion[2] 15000
scoreboard players operation #f le.e = #tier le.e
scoreboard players add #f le.e 6
scoreboard players operation #f le.e *= #6667 le.e
scoreboard players operation #f le.e /= #6 le.e
execute store result storage last_ember:char tmp.f int 1 run scoreboard players get #f le.e
function last_ember:char/arrow_dmg with storage last_ember:char tmp
