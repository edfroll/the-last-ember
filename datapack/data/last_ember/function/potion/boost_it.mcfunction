# storage last_ember:pt: it (the item), pid (potion id without namespace), ty (item id without namespace): boosts the item in place
data remove storage last_ember:pt pc
execute store result score #m le.e run random value 1..4
execute if score #m le.e matches 1 run data modify storage last_ember:pt m set value "u"
execute unless score #m le.e matches 1 run data modify storage last_ember:pt m set value "n"
function last_ember:potion/boost_mac with storage last_ember:pt
execute unless data storage last_ember:pt pc run return 0
data modify storage last_ember:pt it.components."minecraft:potion_contents" set from storage last_ember:pt pc
execute unless data storage last_ember:pt it.components."minecraft:custom_data" run data modify storage last_ember:pt it.components."minecraft:custom_data" set value {}
data modify storage last_ember:pt it.components."minecraft:custom_data" merge value {le_boost:1b}
function last_ember:potion/boost_name with storage last_ember:pt
execute unless data storage last_ember:pt it.components."minecraft:lore" run data modify storage last_ember:pt it.components."minecraft:lore" set value []
data modify storage last_ember:pt it.components."minecraft:lore" append value {text:"Усилено знахарем",color:"gray",italic:false}
