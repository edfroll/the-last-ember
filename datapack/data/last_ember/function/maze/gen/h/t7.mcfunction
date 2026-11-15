# generated: statue 7: the head turns after the player (the face along the way out)
setblock -209 114 -437 minecraft:polished_diorite_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n7 le.mz 0
scoreboard players set #h7 le.mz 1
scoreboard players operation #hr7 le.mz = #gt le.mz
scoreboard players add #hr7 le.mz 1200
