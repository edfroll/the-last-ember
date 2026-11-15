# generated: statue 44: the head turns after the player (the face along the way out)
setblock -161 114 -483 minecraft:polished_diorite_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n44 le.mz 0
scoreboard players set #h44 le.mz 1
scoreboard players operation #hr44 le.mz = #gt le.mz
scoreboard players add #hr44 le.mz 1200
