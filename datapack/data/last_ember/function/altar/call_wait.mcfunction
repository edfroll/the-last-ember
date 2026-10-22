scoreboard players operation #s le.alt = @s le.ecd
scoreboard players operation #s le.alt -= #gt le.e
scoreboard players add #s le.alt 19
scoreboard players operation #s le.alt /= #20 le.e
execute store result storage last_ember:altar w.s int 1 run scoreboard players get #s le.alt
function last_ember:altar/call_wait_m with storage last_ember:altar w
