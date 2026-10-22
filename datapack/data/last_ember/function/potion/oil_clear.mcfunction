# the oil is used up: the oil line is removed, the mark is neutral
data modify storage last_ember:pt it set from entity @s SelectedItem
data remove storage last_ember:pt it.components."minecraft:lore"[-1]
execute unless data storage last_ember:pt it.components."minecraft:lore"[0] run data remove storage last_ember:pt it.components."minecraft:lore"
data modify storage last_ember:pt it.components."minecraft:custom_data".le_oil set value {type:"none",n:0}
function last_ember:potion/oil_write
