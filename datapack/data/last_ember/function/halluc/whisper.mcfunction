# MODULE: as a player at himself: a whisper, steps, a creaking door or a sigh 3-5 blocks BEHIND him. Heard by him only (playsound to @s).
execute store result score #k le.h run random value 0..5
execute if score #k le.h matches 0 positioned ^ ^ ^-4 run playsound minecraft:ambient.cave ambient @s ~ ~ ~ 0.7 0.6
execute if score #k le.h matches 1 positioned ^1 ^ ^-3 run playsound minecraft:block.gravel.step ambient @s ~ ~ ~ 0.9 0.8
execute if score #k le.h matches 2 positioned ^-1 ^ ^-4 run playsound minecraft:block.stone.step ambient @s ~ ~ ~ 0.9 0.8
execute if score #k le.h matches 3 positioned ^ ^ ^-5 run playsound minecraft:block.grass.step ambient @s ~ ~ ~ 0.9 0.7
execute if score #k le.h matches 4 positioned ^1 ^ ^-4 run playsound minecraft:block.wooden_door.open ambient @s ~ ~ ~ 0.6 0.6
execute if score #k le.h matches 5 positioned ^ ^ ^-3 run playsound minecraft:entity.player.breath ambient @s ~ ~ ~ 0.8 0.6
