# generated: statue 65: the head turns after the player (the face along the way out)
setblock -125 114 -449 minecraft:polished_diorite_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n65 le.mz 0
scoreboard players set #h65 le.mz 1
scoreboard players operation #hr65 le.mz = #gt le.mz
scoreboard players add #hr65 le.mz 1200
