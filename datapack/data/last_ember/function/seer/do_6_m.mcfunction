$tag @e[type=#last_ember:monsters,tag=!le.npc,tag=!le.boss,tag=!le.giant,distance=..$(f)] add le.sp_t
$execute as @e[type=#last_ember:neutral,tag=!le.npc,tag=!le.boss,tag=!le.giant,distance=..$(f)] if function last_ember:seer/is_angry run tag @s add le.sp_t
$tag @e[tag=le.sp_t,distance=$(a)..] add le.sp_far
execute as @e[tag=le.sp_t] at @s run function last_ember:seer/banish_one
tag @e[tag=le.sp_t] remove le.sp_t
tag @e[tag=le.sp_far] remove le.sp_far
