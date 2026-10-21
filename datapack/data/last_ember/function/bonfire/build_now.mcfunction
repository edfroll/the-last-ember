# at the hearth position (macro i): the standard bonfire of its variant + interactions; eternal (main) bonfires are lit from the start
$scoreboard players set #i le.e $(i)
$data modify storage last_ember:bt b set from storage last_ember:bonfires by.b$(i)
function last_ember:bonfire/build_variant with storage last_ember:bt b
$data modify storage last_ember:bonfires by.b$(i).built set value 1b
$execute if data storage last_ember:bonfires by.b$(i){eternal:1b} run function last_ember:bonfire/set_lit with storage last_ember:bonfires by.b$(i)
$execute if data storage last_ember:bonfires by.b$(i){state:1} run function last_ember:bonfire/set_lit with storage last_ember:bonfires by.b$(i)
