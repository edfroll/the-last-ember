# MODULE: as a player: a short pulse, nausea (4 s) or darkness (3 s); they run out by themselves
execute store result score #k le.h run random value 0..1
execute if score #k le.h matches 0 run effect give @s minecraft:nausea 4 0 true
execute if score #k le.h matches 1 run effect give @s minecraft:darkness 3 0 true
