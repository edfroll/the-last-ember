# as a player
function last_ember:bonfire/give_cauldron
give @s minecraft:stone_sword[minecraft:custom_name={"text":"Нож знахаря","color":"gray","italic":false},minecraft:custom_data={le_keep:1b},minecraft:lore=[{"text":"Короткий клинок: бьёт быстро и слабо.","color":"gray","italic":false}],minecraft:attribute_modifiers=[{type:"minecraft:attack_damage",id:"last_ember:dagger_damage",amount:2,operation:"add_value",slot:"mainhand"},{type:"minecraft:attack_speed",id:"last_ember:dagger_speed",amount:-2,operation:"add_value",slot:"mainhand"}]] 1
give @s minecraft:glass_bottle 3
give @s minecraft:potion[minecraft:potion_contents={potion:"minecraft:healing"}] 2
give @s minecraft:brown_mushroom 4
give @s minecraft:sugar 2
