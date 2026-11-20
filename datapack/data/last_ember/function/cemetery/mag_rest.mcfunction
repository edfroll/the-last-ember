# T-027: the Magister is laid to rest (killed, or the peaceful difficulty): the quest at 4, the lid aside, the seal in the sarcophagus,
# chest 2 unlocked, the exit open, 50 points of experience; never comes back
execute if score #mg le.cem matches 2 run return 0
scoreboard players set #mg le.cem 2
scoreboard players set #q le.cem 4
execute if score #ss le.cem matches 0 run scoreboard players set #ss le.cem 1
kill @e[type=minecraft:skeleton,tag=le.cmag]
execute as @e[tag=le.cspirit] at @s run function last_ember:cemetery/spirit_gone
function last_ember:cemetery/gen/lid_open
function last_ember:cemetery/gen/chest_unlock
function last_ember:cemetery/gen/bars_open
function last_ember:cemetery/gen/mag_seal
function last_ember:cemetery/gen/mag_xp
function last_ember:cemetery/gen/rest_fx
function last_ember:cemetery/save
