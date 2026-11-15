# generated: statue 8: the head turns after the player (the face along the way out)
setblock -197 114 -425 minecraft:polished_diorite_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n8 le.mz 0
scoreboard players set #h8 le.mz 1
scoreboard players operation #hr8 le.mz = #gt le.mz
scoreboard players add #hr8 le.mz 1200
