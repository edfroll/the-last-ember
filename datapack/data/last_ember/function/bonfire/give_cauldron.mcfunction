# the healer's cauldron (class item: kept on death via le_keep). The class system will hand it out; for tests: function last_ember:bonfire/give_cauldron
give @s minecraft:cauldron[minecraft:custom_data={le_cauldron:1b,le_keep:1b},minecraft:custom_name={"text":"Котёл знахаря","italic":false,"color":"green"}] 1
tag @s add le.class.healer
