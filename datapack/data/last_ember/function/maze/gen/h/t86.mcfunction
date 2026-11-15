# generated: statue 86: the head turns after the player (the face along the way out)
setblock -109 114 -421 minecraft:polished_diorite_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n86 le.mz 0
scoreboard players set #h86 le.mz 1
scoreboard players operation #hr86 le.mz = #gt le.mz
scoreboard players add #hr86 le.mz 1200
