# once a second, as a wearer: the fee grows with the time (continuous wearing)
scoreboard players operation #e le.e = #gt le.e
scoreboard players operation #e le.e -= @s le.rt
scoreboard players operation #e le.e /= #20 le.e
execute if score #e le.e matches 10.. if predicate last_ember:chance_30 run function last_ember:ring/whisper
execute if score #e le.e matches 20.. run effect give @s minecraft:darkness 4 0 true
execute if score #e le.e matches 20.. run effect give @s minecraft:slowness 2 0 true
execute if score #e le.e matches 30..39 run effect give @s minecraft:wither 3 0 true
execute if score #e le.e matches 40.. run effect give @s minecraft:wither 3 1 true
