$execute unless data storage last_ember:ash t.t$(id) run return 0
$data modify storage last_ember:dt rec set from storage last_ember:ash t.t$(id)
$data remove storage last_ember:ash t.t$(id)
$scoreboard players set #k le.e $(id)
execute as @e[tag=le.ash] if score @s le.tid = #k le.e at @s run function last_ember:ash/remove_entity
function last_ember:urn/add with storage last_ember:dt rec
