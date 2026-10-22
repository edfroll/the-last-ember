$tag @e[type=#last_ember:monsters,tag=!le.npc,distance=..$(r)] add le.sp_t
$execute as @e[type=#last_ember:neutral,tag=!le.npc,distance=..$(r)] if function last_ember:seer/is_angry run tag @s add le.sp_t
$effect give @e[tag=le.sp_t] minecraft:slowness 10 $(a) true
$effect give @e[tag=le.sp_t] minecraft:weakness 10 $(a) true
scoreboard players operation @e[tag=le.sp_t] le.frz = #gt le.e
scoreboard players add @e[tag=le.sp_t] le.frz 200
tag @e[tag=le.sp_t] add le.frost
execute as @e[tag=le.sp_t] at @s run particle minecraft:snowflake ~ ~1 ~ 0.3 0.5 0.3 0.02 12
tag @e[tag=le.sp_t] remove le.sp_t
function last_ember:seer/frost_loop
