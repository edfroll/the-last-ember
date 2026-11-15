# generated: statue 10: the head turns after the player (the face along the way out)
setblock -194 114 -421 minecraft:polished_diorite_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n10 le.mz 0
scoreboard players set #h10 le.mz 1
scoreboard players operation #hr10 le.mz = #gt le.mz
scoreboard players add #hr10 le.mz 1200
