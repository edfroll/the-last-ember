# the Ashen Cover: Absorption for the seer (4 hearts) and for the players around (2 hearts); radius 6 (tier 0) .. 10 (tier 6), time 15 .. 25 s
scoreboard players operation #r le.e = @s le.tier
scoreboard players operation #r le.e *= #4 le.e
scoreboard players operation #r le.e /= #6 le.e
scoreboard players add #r le.e 6
scoreboard players operation #d le.e = @s le.tier
scoreboard players operation #d le.e *= #10 le.e
scoreboard players operation #d le.e /= #6 le.e
scoreboard players add #d le.e 15
execute store result storage last_ember:seer c.r int 1 run scoreboard players get #r le.e
execute store result storage last_ember:seer c.d int 1 run scoreboard players get #d le.e
tag @s add le.caster
function last_ember:seer/do_1_m with storage last_ember:seer c
tag @s remove le.caster
particle minecraft:wax_on ~ ~1 ~ 0.4 0.7 0.4 0.3 40
particle minecraft:end_rod ~ ~1 ~ 0.3 0.8 0.3 0.05 20
playsound minecraft:block.beacon.power_select player @a[distance=..16] ~ ~ ~ 0.8 1.6
return 1
