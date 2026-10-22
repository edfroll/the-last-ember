$tag @e[type=#last_ember:monsters,tag=!le.npc,tag=!le.boss,tag=!le.giant,distance=..$(r)] add le.sp_t
$execute as @e[type=#last_ember:neutral,tag=!le.npc,tag=!le.boss,tag=!le.giant,distance=..$(r)] if function last_ember:seer/is_angry run tag @s add le.sp_t
execute as @e[tag=le.sp_t] run data modify entity @s Motion[1] set from storage last_ember:seer c.v
execute as @e[tag=le.sp_t] at @s run particle minecraft:cloud ~ ~0.2 ~ 0.3 0.1 0.3 0.05 8
tag @e[tag=le.sp_t] remove le.sp_t
