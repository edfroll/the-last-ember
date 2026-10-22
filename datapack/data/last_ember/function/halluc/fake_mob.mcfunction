# MODULE: as a player at himself: the sound of a mob that is not there, 5-9 blocks off. Heard by him only.
execute store result score #k le.h run random value 0..3
execute if score #k le.h matches 0 positioned ^5 ^ ^4 run playsound minecraft:entity.zombie.ambient hostile @s ~ ~ ~ 0.8 0.8
execute if score #k le.h matches 1 positioned ^-6 ^ ^3 run playsound minecraft:entity.spider.ambient hostile @s ~ ~ ~ 0.8 0.9
execute if score #k le.h matches 2 positioned ^3 ^ ^-7 run playsound minecraft:entity.skeleton.step hostile @s ~ ~ ~ 0.9 0.9
execute if score #k le.h matches 3 positioned ^-4 ^ ^6 run playsound minecraft:entity.skeleton.ambient hostile @s ~ ~ ~ 0.7 0.8
