# a thrown potion of a healer flies 1.5x farther (the speed factor is measured: tools/test_class.py throw)
tag @s add le.ar
scoreboard players set #hl le.e 0
execute on origin if entity @s[type=minecraft:player,tag=le.class.healer] run scoreboard players set #hl le.e 1
execute if score #hl le.e matches 1 run function last_ember:char/potion_fast
