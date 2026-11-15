# generated: statue 11: the head turns after the player (the face along the way out)
setblock -200 114 -412 minecraft:polished_diorite_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n11 le.mz 0
scoreboard players set #h11 le.mz 1
scoreboard players operation #hr11 le.mz = #gt le.mz
scoreboard players add #hr11 le.mz 1200
