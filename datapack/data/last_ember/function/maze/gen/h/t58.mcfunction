# generated: statue 58: the head turns after the player (the face along the way out)
setblock -122 114 -445 minecraft:polished_diorite_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n58 le.mz 0
scoreboard players set #h58 le.mz 1
scoreboard players operation #hr58 le.mz = #gt le.mz
scoreboard players add #hr58 le.mz 1200
