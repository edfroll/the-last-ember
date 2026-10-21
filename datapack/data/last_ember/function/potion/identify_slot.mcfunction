# macro slot: a murky vial in a healer's inventory shows what it is: the usual name, the effects, the mark is removed
$data modify storage last_ember:pt it set from entity @s Inventory[{Slot:$(slot)b}]
data modify storage last_ember:pt eid set string storage last_ember:pt it.components."minecraft:potion_contents".custom_effects[0].id 10
data remove storage last_ember:pt it.components."minecraft:custom_data".le_murky
data remove storage last_ember:pt it.components."minecraft:tooltip_display"
function last_ember:potion/identify_name with storage last_ember:pt
execute unless data storage last_ember:pt it.components."minecraft:lore" run data modify storage last_ember:pt it.components."minecraft:lore" set value []
data modify storage last_ember:pt it.components."minecraft:lore" append value {text:"Опознано знахарем",color:"gray",italic:false}
$function last_ember:potion/put {slot:$(slot)}
title @s actionbar {"text":"Склянка опознана","color":"green"}
