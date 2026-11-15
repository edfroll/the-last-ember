# generated: statue 45: the head turns after the player (the face along the way out)
setblock -146 114 -489 minecraft:polished_diorite_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n45 le.mz 0
scoreboard players set #h45 le.mz 1
scoreboard players operation #hr45 le.mz = #gt le.mz
scoreboard players add #hr45 le.mz 1200
