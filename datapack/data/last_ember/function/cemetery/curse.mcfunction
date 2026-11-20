# T-027: as a player, every second: the curses of the things from the graves work only while worn (armour) or held (either hand);
# short effects (3 s) renewed every second, the blood every 20 s, the darkness every 30 s
execute unless items entity @s armor.* *[minecraft:custom_data~{le_cursed:1b}] unless items entity @s weapon.* *[minecraft:custom_data~{le_cursed:1b}] run return 0
scoreboard players operation #s20 le.cem = #sec le.cem
scoreboard players operation #s20 le.cem %= #20 le.cem
scoreboard players operation #s30 le.cem = #sec le.cem
scoreboard players operation #s30 le.cem %= #30 le.cem
execute if score #s20 le.cem matches 0 if items entity @s armor.* *[minecraft:custom_data~{le_cursed:1b,le_curse:"blood"}] run function last_ember:cemetery/curse_blood
execute if score #s20 le.cem matches 0 if items entity @s weapon.* *[minecraft:custom_data~{le_cursed:1b,le_curse:"blood"}] run function last_ember:cemetery/curse_blood
execute if items entity @s armor.* *[minecraft:custom_data~{le_cursed:1b,le_curse:"weight"}] run effect give @s minecraft:slowness 3 0 true
execute if items entity @s weapon.* *[minecraft:custom_data~{le_cursed:1b,le_curse:"weight"}] run effect give @s minecraft:slowness 3 0 true
execute if score #s30 le.cem matches 0 if items entity @s armor.* *[minecraft:custom_data~{le_cursed:1b,le_curse:"dark"}] run effect give @s minecraft:darkness 3 0 true
execute if score #s30 le.cem matches 0 if items entity @s weapon.* *[minecraft:custom_data~{le_cursed:1b,le_curse:"dark"}] run effect give @s minecraft:darkness 3 0 true
execute if items entity @s armor.* *[minecraft:custom_data~{le_cursed:1b,le_curse:"hunger"}] run effect give @s minecraft:hunger 3 0 true
execute if items entity @s weapon.* *[minecraft:custom_data~{le_cursed:1b,le_curse:"hunger"}] run effect give @s minecraft:hunger 3 0 true
execute if items entity @s armor.* *[minecraft:custom_data~{le_cursed:1b,le_curse:"weak"}] run effect give @s minecraft:weakness 3 0 true
execute if items entity @s weapon.* *[minecraft:custom_data~{le_cursed:1b,le_curse:"weak"}] run effect give @s minecraft:weakness 3 0 true
