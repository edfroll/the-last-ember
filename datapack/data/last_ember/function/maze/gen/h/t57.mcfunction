# generated: statue 57: the head turns after the player (the face along the way out)
setblock -125 114 -455 minecraft:polished_diorite_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n57 le.mz 0
scoreboard players set #h57 le.mz 1
scoreboard players operation #hr57 le.mz = #gt le.mz
scoreboard players add #hr57 le.mz 1200
