# generated: statue 27: the head turns after the player (the face along the way out)
setblock -164 114 -445 minecraft:polished_diorite_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n27 le.mz 0
scoreboard players set #h27 le.mz 1
scoreboard players operation #hr27 le.mz = #gt le.mz
scoreboard players add #hr27 le.mz 1200
