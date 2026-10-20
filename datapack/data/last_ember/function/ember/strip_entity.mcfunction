execute if items entity @s contents *[minecraft:custom_data~{le_ember:1b}] run item replace entity @s contents with minecraft:air
execute if items entity @s weapon.mainhand *[minecraft:custom_data~{le_ember:1b}] run item replace entity @s weapon.mainhand with minecraft:air
execute if items entity @s weapon.offhand *[minecraft:custom_data~{le_ember:1b}] run item replace entity @s weapon.offhand with minecraft:air
execute if items entity @s armor.head *[minecraft:custom_data~{le_ember:1b}] run item replace entity @s armor.head with minecraft:air
execute if items entity @s container.* *[minecraft:custom_data~{le_ember:1b}] run function last_ember:ember/strip_entity_container
