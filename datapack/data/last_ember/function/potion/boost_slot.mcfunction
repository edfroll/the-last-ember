# macro slot: as a healer, a potion in container slot $(slot) without le_boost -> boosted (duration x1.5, 25%: level +1 up to II), mark le_boost
$data modify storage last_ember:pt it set from entity @s Inventory[{Slot:$(slot)b}]
execute unless data storage last_ember:pt it.components."minecraft:potion_contents".potion run return 0
data modify storage last_ember:pt pid set string storage last_ember:pt it.components."minecraft:potion_contents".potion 10
data modify storage last_ember:pt ty set string storage last_ember:pt it.id 10
function last_ember:potion/boost_it
execute unless data storage last_ember:pt pc run return 0
$function last_ember:potion/put {slot:$(slot)}
