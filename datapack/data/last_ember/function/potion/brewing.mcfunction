# as a brewing cauldron: bubbles, steam; items are pushed out; at the end the result appears
scoreboard players remove @s le.ctimer 1
particle minecraft:bubble_pop ~ ~0.8 ~ 0.25 0.05 0.25 0.02 6
particle minecraft:cloud ~ ~1.1 ~ 0.15 0.1 0.15 0.01 1
execute if score @s le.ctimer matches 20 run playsound minecraft:block.brewing_stand.brew block @a[distance=..12] ~ ~ ~ 0.8 1
execute positioned ~ ~0.45 ~ as @e[type=minecraft:item,distance=..0.9] at @s run function last_ember:potion/eject
execute if score @s le.ctimer matches ..0 run function last_ember:potion/brew_done
