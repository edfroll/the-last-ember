# macro n: the spell n is cooling down: a short dull sound and the seconds left
$scoreboard players operation #r le.e = @s le.cd$(n)
scoreboard players operation #r le.e -= #gt le.e
scoreboard players add #r le.e 19
scoreboard players operation #r le.e /= #20 le.e
execute store result storage last_ember:seer h.secs int 1 run scoreboard players get #r le.e
function last_ember:seer/cd_msg_m with storage last_ember:seer h
playsound minecraft:block.note_block.basedrum player @s ~ ~ ~ 0.7 0.6
