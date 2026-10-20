# as a player: 1 if the Ember is directly in inventory, off-hand or on the cursor
execute if items entity @s container.* *[minecraft:custom_data~{le_ember:1b}] run return 1
execute if items entity @s weapon.offhand *[minecraft:custom_data~{le_ember:1b}] run return 1
execute if items entity @s player.cursor *[minecraft:custom_data~{le_ember:1b}] run return 1
return 0
