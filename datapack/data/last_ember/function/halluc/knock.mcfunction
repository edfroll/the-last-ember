# as a player: a "blow": a hurt sound and a short shake of the screen (0.5 heart; never below 1 heart)
execute store result score #hp le.h run data get entity @s Health
execute if score #hp le.h matches ..2 run return 0
damage @s 1 minecraft:magic
