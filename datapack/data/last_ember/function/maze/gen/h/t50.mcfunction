# generated: statue 50: the head turns after the player (the face along the way out)
setblock -141 114 -411 minecraft:polished_diorite_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n50 le.mz 0
scoreboard players set #h50 le.mz 1
scoreboard players operation #hr50 le.mz = #gt le.mz
scoreboard players add #hr50 le.mz 1200
