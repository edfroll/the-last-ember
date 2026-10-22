# reward of using_item (every tick while a stick is being used): the staff of a seer. The horn, an oil or a staff in other hands: nothing.
advancement revoke @s only last_ember:seer/using
execute unless entity @s[tag=le.class.seer] run return 0
execute unless items entity @s weapon.mainhand *[minecraft:custom_data~{le_staff:"blink"}] unless items entity @s weapon.mainhand *[minecraft:custom_data~{le_staff:"frost"}] unless items entity @s weapon.mainhand *[minecraft:custom_data~{le_staff:"flame"}] unless items entity @s weapon.mainhand *[minecraft:custom_data~{le_staff:"lift"}] unless items entity @s weapon.mainhand *[minecraft:custom_data~{le_staff:"banish"}] unless items entity @s weapon.mainhand *[minecraft:custom_data~{le_staff:"wrath"}] run return 0
scoreboard players operation @s le.slast = #gt le.e
scoreboard players add @s le.suse 1
execute if score @s le.suse matches 1 run function last_ember:seer/use_start
execute if score @s le.suse matches 2.. if score @s le.wchg matches 0.. run function last_ember:seer/wrath_hold
