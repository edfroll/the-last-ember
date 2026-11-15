# generated: statue 2: the head turns after the player (the face along the way out)
setblock -188 114 -445 minecraft:polished_diorite_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n2 le.mz 0
scoreboard players set #h2 le.mz 1
scoreboard players operation #hr2 le.mz = #gt le.mz
scoreboard players add #hr2 le.mz 1200
