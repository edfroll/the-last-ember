# generated: statue 72: the head turns after the player (the face along the way out)
setblock -122 114 -407 minecraft:polished_diorite_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n72 le.mz 0
scoreboard players set #h72 le.mz 1
scoreboard players operation #hr72 le.mz = #gt le.mz
scoreboard players add #hr72 le.mz 1200
