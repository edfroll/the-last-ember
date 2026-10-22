# as the carrier at himself
scoreboard players operation #c le.alt = #chapters le.alt
execute if score #c le.alt matches ..0 run return run function last_ember:altar/light_off
execute if score #c le.alt matches 1.. if items entity @s weapon.mainhand *[minecraft:custom_data~{le_ember:1b}] run function last_ember:altar/light_here
execute if score #c le.alt matches 1.. unless items entity @s weapon.mainhand *[minecraft:custom_data~{le_ember:1b}] unless items entity @s weapon.offhand *[minecraft:custom_data~{le_ember:1b}] run function last_ember:altar/light_off
execute if score #c le.alt matches 1.. unless items entity @s weapon.mainhand *[minecraft:custom_data~{le_ember:1b}] if items entity @s weapon.offhand *[minecraft:custom_data~{le_ember:1b}] run function last_ember:altar/light_here
execute unless function last_ember:ember/has run return 0
execute if score #c le.alt matches 2.. run tag @a[distance=..6,gamemode=!spectator] add le.warm
execute if score #c le.alt matches 4.. as @a[distance=..6,gamemode=!spectator] run effect clear @s minecraft:darkness
execute if score #c le.alt matches 5.. as @a[distance=..6,gamemode=!spectator] at @s unless block ~ ~ ~ minecraft:lava unless block ~ ~0.6 ~ minecraft:lava run effect give @s minecraft:fire_resistance 1 0 true
