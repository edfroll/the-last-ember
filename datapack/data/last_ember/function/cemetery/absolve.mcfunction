# T-027: «Отпеть вещь в руке»: after the Magister (#q 4): the cursed thing in the main hand + a Trophy of the Dale -> the curse is gone
execute unless score #q le.cem matches 4 run return 0
execute unless items entity @s weapon.mainhand *[minecraft:custom_data~{le_cursed:1b}] run return run tellraw @s [{"text":"Смотритель: ","color":"gray"},{"text":"В руке у тебя ничего чужого.","color":"white"}]
execute store result score #c le.cem run clear @s *[minecraft:custom_data~{le_trophy:"r1"}] 0
execute if score #c le.cem matches 0 run return run tellraw @s [{"text":"Смотритель: ","color":"gray"},{"text":"Мёртвые денег не берут. Я беру. Трофей Дола.","color":"white"}]
clear @s *[minecraft:custom_data~{le_trophy:"r1"}] 1
item modify entity @s weapon.mainhand last_ember:cemetery/absolve
particle minecraft:soul ~ ~1.2 ~ 0.4 0.5 0.4 0.03 20 force
playsound minecraft:block.bell.resonate player @a[distance=..12] ~ ~ ~ 0.6 1.2
tellraw @s [{"text":"Смотритель: ","color":"gray"},{"text":"Ушёл. Носи.","color":"white"}]
