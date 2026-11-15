# generated: statue 20: the head turns after the player (the face along the way out)
setblock -185 114 -465 minecraft:polished_diorite_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n20 le.mz 0
scoreboard players set #h20 le.mz 1
scoreboard players operation #hr20 le.mz = #gt le.mz
scoreboard players add #hr20 le.mz 1200
