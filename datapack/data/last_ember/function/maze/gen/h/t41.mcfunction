# generated: statue 41: the head turns after the player (the face along the way out)
setblock -168 114 -397 minecraft:polished_diorite_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n41 le.mz 0
scoreboard players set #h41 le.mz 1
scoreboard players operation #hr41 le.mz = #gt le.mz
scoreboard players add #hr41 le.mz 1200
