# generated: statue 40: the head turns after the player (the face along the way out)
setblock -185 114 -397 minecraft:polished_diorite_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n40 le.mz 0
scoreboard players set #h40 le.mz 1
scoreboard players operation #hr40 le.mz = #gt le.mz
scoreboard players add #hr40 le.mz 1200
