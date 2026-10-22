# as a seer: #sel le.e = the number of the selected spell (1 = the Ashen Cover, else the staff's own)
scoreboard players set #sel le.e 1
execute if score @s le.spsel matches 1 run return 1
execute if items entity @s weapon.mainhand *[minecraft:custom_data~{le_staff:"blink"}] run scoreboard players set #sel le.e 2
execute if items entity @s weapon.mainhand *[minecraft:custom_data~{le_staff:"frost"}] run scoreboard players set #sel le.e 3
execute if items entity @s weapon.mainhand *[minecraft:custom_data~{le_staff:"flame"}] run scoreboard players set #sel le.e 4
execute if items entity @s weapon.mainhand *[minecraft:custom_data~{le_staff:"lift"}] run scoreboard players set #sel le.e 5
execute if items entity @s weapon.mainhand *[minecraft:custom_data~{le_staff:"banish"}] run scoreboard players set #sel le.e 6
execute if items entity @s weapon.mainhand *[minecraft:custom_data~{le_staff:"wrath"}] run scoreboard players set #sel le.e 7
