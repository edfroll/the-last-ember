# no weapon in the main hand: the oil comes back
title @s actionbar {"text":"Масло: нужен клинок в основной руке","color":"red"}
execute if data storage last_ember:pt {oil:"poison"} run function last_ember:potion/give_oil_poison
execute if data storage last_ember:pt {oil:"fire"} run function last_ember:potion/give_oil_fire
