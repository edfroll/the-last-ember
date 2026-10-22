# as a seer holding a staff: the staff's own spell
execute if items entity @s weapon.mainhand *[minecraft:custom_data~{le_staff:"blink"}] run return run function last_ember:seer/cast_2
execute if items entity @s weapon.mainhand *[minecraft:custom_data~{le_staff:"frost"}] run return run function last_ember:seer/cast_3
execute if items entity @s weapon.mainhand *[minecraft:custom_data~{le_staff:"flame"}] run return run function last_ember:seer/cast_4
execute if items entity @s weapon.mainhand *[minecraft:custom_data~{le_staff:"lift"}] run return run function last_ember:seer/cast_5
execute if items entity @s weapon.mainhand *[minecraft:custom_data~{le_staff:"banish"}] run return run function last_ember:seer/cast_6
execute if items entity @s weapon.mainhand *[minecraft:custom_data~{le_staff:"wrath"}] run return run function last_ember:seer/cast_7
