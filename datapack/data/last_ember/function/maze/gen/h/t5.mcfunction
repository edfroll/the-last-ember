# generated: statue 5: the head turns after the player (the face along the way out)
setblock -194 114 -421 minecraft:polished_diorite_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n5 le.mz 0
scoreboard players set #h5 le.mz 1
scoreboard players operation #hr5 le.mz = #gt le.mz
scoreboard players add #hr5 le.mz 1200
