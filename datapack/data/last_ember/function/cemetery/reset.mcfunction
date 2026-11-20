# T-027: ADMIN/TEST: the cemetery and the lodge as in a new world (the graves closed, the unrest 0, the quest not taken, the door shut,
# the key in Thane's coffin, the Magister asleep, the lid / chest 2 / the exit closed, the quest items of the players gone, not faded)
function last_ember:cemetery/gen/fresh
function last_ember:cemetery/gen/init
clear @a *[minecraft:custom_data~{le_citem:"cem_shovel"}]
clear @a *[minecraft:custom_data~{le_citem:"crypt_key"}]
clear @a *[minecraft:custom_data~{le_citem:"seal"}]
kill @e[type=minecraft:item,tag=!le.kitem] 
kill @e[type=minecraft:skeleton,tag=le.cmag]
execute as @e[tag=le.cspirit] at @s run function last_ember:cemetery/spirit_gone
kill @e[type=minecraft:item_display,tag=le.csealdisp]
kill @e[type=minecraft:interaction,tag=le.cseal]
function last_ember:cemetery/gen/graves_reset
function last_ember:cemetery/gen/lid_closed
function last_ember:cemetery/gen/chest_lock
function last_ember:cemetery/gen/bars_close
function last_ember:cemetery/gen/door_set
function last_ember:cemetery/gen/unfade_apply
scoreboard players set #bellcd le.cem 0
scoreboard players reset @a le.cspy
scoreboard players reset @a le.cspc
