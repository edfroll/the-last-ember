# generated: statue 73: the head turns after the player (the face along the way out)
setblock -125 114 -412 minecraft:polished_diorite_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n73 le.mz 0
scoreboard players set #h73 le.mz 1
scoreboard players operation #hr73 le.mz = #gt le.mz
scoreboard players add #hr73 le.mz 1200
