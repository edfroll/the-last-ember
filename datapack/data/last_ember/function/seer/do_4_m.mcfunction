$tag @e[type=#last_ember:monsters,tag=!le.npc,distance=..$(r)] add le.sp_t
execute as @e[tag=le.sp_t] run data modify entity @s Fire set value 100s
execute as @e[tag=le.sp_t] at @s run function last_ember:seer/fire_one
tag @e[tag=le.sp_t] remove le.sp_t
function last_ember:seer/fire_loop
