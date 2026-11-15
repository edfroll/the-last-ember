# generated: statue 16: the head turns after the player (the face along the way out)
setblock -185 114 -465 minecraft:polished_diorite_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n16 le.mz 0
scoreboard players set #h16 le.mz 1
scoreboard players operation #hr16 le.mz = #gt le.mz
scoreboard players add #hr16 le.mz 1200
