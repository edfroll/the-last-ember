# generated: statue 38: the head turns after the player (the face along the way out)
setblock -164 114 -397 minecraft:polished_diorite_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n38 le.mz 0
scoreboard players set #h38 le.mz 1
scoreboard players operation #hr38 le.mz = #gt le.mz
scoreboard players add #hr38 le.mz 1200
