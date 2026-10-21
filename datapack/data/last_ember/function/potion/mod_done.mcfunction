# as the cauldron: modifier brew (le.crec 101 longer, 102 stronger, 103 splash, 104 lingering): the stored potion comes out modified
execute store result storage last_ember:cauldron i int 1 run scoreboard players get @s le.bidx
function last_ember:potion/load_pot with storage last_ember:cauldron
execute if data storage last_ember:pt it.components."minecraft:potion_contents".potion run function last_ember:potion/pot_to_custom
execute if score @s le.crec matches 101 run function last_ember:potion/mod_longer
execute if score @s le.crec matches 102 run function last_ember:potion/mod_stronger
execute if score @s le.crec matches 103 run data modify storage last_ember:pt it.id set value "minecraft:splash_potion"
execute if score @s le.crec matches 104 run data modify storage last_ember:pt it.id set value "minecraft:lingering_potion"
execute unless data storage last_ember:pt it.components."minecraft:custom_data" run data modify storage last_ember:pt it.components."minecraft:custom_data" set value {}
data modify storage last_ember:pt it.components."minecraft:custom_data" merge value {le_mod:1b}
execute unless data storage last_ember:pt it.components."minecraft:lore" run data modify storage last_ember:pt it.components."minecraft:lore" set value []
execute if score @s le.crec matches 101 run data modify storage last_ember:pt it.components."minecraft:lore" append value {text:"Модификатор: дольше",color:"gray",italic:false}
execute if score @s le.crec matches 102 run data modify storage last_ember:pt it.components."minecraft:lore" append value {text:"Модификатор: сильнее",color:"gray",italic:false}
execute if score @s le.crec matches 103 run data modify storage last_ember:pt it.components."minecraft:lore" append value {text:"Модификатор: взрывное",color:"gray",italic:false}
execute if score @s le.crec matches 104 run data modify storage last_ember:pt it.components."minecraft:lore" append value {text:"Модификатор: туманное",color:"gray",italic:false}
function last_ember:potion/emit_one
