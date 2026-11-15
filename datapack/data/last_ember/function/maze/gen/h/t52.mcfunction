# generated: statue 52: the head turns after the player (the face along the way out)
setblock -161 114 -373 minecraft:polished_diorite_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n52 le.mz 0
scoreboard players set #h52 le.mz 1
scoreboard players operation #hr52 le.mz = #gt le.mz
scoreboard players add #hr52 le.mz 1200
