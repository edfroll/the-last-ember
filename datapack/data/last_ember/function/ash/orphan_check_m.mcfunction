$execute if data storage last_ember:ash t.t$(id) run return 0
$scoreboard players set #k le.e $(id)
execute as @e[tag=le.ash] if score @s le.tid = #k le.e at @s run function last_ember:ash/remove_entity
