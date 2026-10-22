scoreboard players operation #s le.e = @s le.rcd
scoreboard players operation #s le.e -= #gt le.e
scoreboard players add #s le.e 19
scoreboard players operation #s le.e /= #20 le.e
execute store result storage last_ember:ring msg.s int 1 run scoreboard players get #s le.e
function last_ember:ring/refuse_cd_m with storage last_ember:ring msg
