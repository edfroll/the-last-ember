# generated: statue 67: the head turns after the player (the face along the way out)
setblock -132 114 -435 minecraft:polished_diorite_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n67 le.mz 0
scoreboard players set #h67 le.mz 1
scoreboard players operation #hr67 le.mz = #gt le.mz
scoreboard players add #hr67 le.mz 1200
