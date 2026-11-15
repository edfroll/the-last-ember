# generated: statue 62: the head turns after the player (the face along the way out)
setblock -117 114 -465 minecraft:polished_diorite_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n62 le.mz 0
scoreboard players set #h62 le.mz 1
scoreboard players operation #hr62 le.mz = #gt le.mz
scoreboard players add #hr62 le.mz 1200
