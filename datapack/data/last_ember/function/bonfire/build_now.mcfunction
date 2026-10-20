# at the hearth position (macro i): blocks + interactions; eternal (main) bonfires are lit from the start
$scoreboard players set #i le.e $(i)
function last_ember:bonfire/build_here
$data modify storage last_ember:bonfires by.b$(i).built set value 1b
$execute if data storage last_ember:bonfires by.b$(i){eternal:1b} run function last_ember:bonfire/set_lit {i:$(i)}
$execute if data storage last_ember:bonfires by.b$(i){state:1} run function last_ember:bonfire/set_lit {i:$(i)}
