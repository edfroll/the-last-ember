# generated: statue 64: the head turns after the player (the face along the way out)
setblock -133 114 -460 minecraft:polished_diorite_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n64 le.mz 0
scoreboard players set #h64 le.mz 1
scoreboard players operation #hr64 le.mz = #gt le.mz
scoreboard players add #hr64 le.mz 1200
