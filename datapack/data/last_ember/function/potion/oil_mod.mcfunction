# macro oil, n, sfx ("_a" = put on: the oil line is appended; "_r" = the count changed: the last lore line is replaced): the weapon in the main hand
# gets le_oil {type, n} and ITS OWN LAST LORE LINE "Масло …: N ударов" (the weapon's other lore is left alone)
data modify storage last_ember:pt it set from entity @s SelectedItem
execute unless data storage last_ember:pt it.components."minecraft:lore" run data modify storage last_ember:pt it.components."minecraft:lore" set value []
execute unless data storage last_ember:pt it.components."minecraft:custom_data" run data modify storage last_ember:pt it.components."minecraft:custom_data" set value {}
execute if data storage last_ember:pt {sfx:"_r"} run data remove storage last_ember:pt it.components."minecraft:lore"[-1]
$data modify storage last_ember:pt it.components."minecraft:custom_data".le_oil set value {type:"$(oil)",n:$(n)}
data modify storage last_ember:pt word set value "ударов"
execute if score #n le.e matches 1 run data modify storage last_ember:pt word set value "удар"
execute if score #n le.e matches 2..4 run data modify storage last_ember:pt word set value "удара"
execute if data storage last_ember:pt {oil:"poison"} run data modify storage last_ember:pt label set value "яда"
execute if data storage last_ember:pt {oil:"fire"} run data modify storage last_ember:pt label set value "огня"
function last_ember:potion/oil_line with storage last_ember:pt
function last_ember:potion/oil_write
