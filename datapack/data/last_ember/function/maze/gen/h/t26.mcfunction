# generated: statue 26: the head turns after the player (the face along the way out)
setblock -185 114 -461 minecraft:polished_diorite_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n26 le.mz 0
scoreboard players set #h26 le.mz 1
scoreboard players operation #hr26 le.mz = #gt le.mz
scoreboard players add #hr26 le.mz 1200
