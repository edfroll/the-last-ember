# macro id gen, as a player: when the valid key is on him he is the last holder (inventory, hands, cursor, armor slots, ender chest)
$execute if items entity @s container.* *[minecraft:custom_data~{le_key:"$(id)",gen:$(gen)}] run return run function last_ember:altar/key_held {id:"$(id)"}
$execute if items entity @s weapon.offhand *[minecraft:custom_data~{le_key:"$(id)",gen:$(gen)}] run return run function last_ember:altar/key_held {id:"$(id)"}
$execute if items entity @s player.cursor *[minecraft:custom_data~{le_key:"$(id)",gen:$(gen)}] run return run function last_ember:altar/key_held {id:"$(id)"}
$execute if items entity @s armor.* *[minecraft:custom_data~{le_key:"$(id)",gen:$(gen)}] run return run function last_ember:altar/key_held {id:"$(id)"}
$execute if items entity @s enderchest.* *[minecraft:custom_data~{le_key:"$(id)",gen:$(gen)}] run return run function last_ember:altar/key_held {id:"$(id)"}
return 0
