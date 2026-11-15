# generated: statue 82: the head turns after the player (the face along the way out)
setblock -107 114 -421 minecraft:polished_diorite_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n82 le.mz 0
scoreboard players set #h82 le.mz 1
scoreboard players operation #hr82 le.mz = #gt le.mz
scoreboard players add #hr82 le.mz 1200
