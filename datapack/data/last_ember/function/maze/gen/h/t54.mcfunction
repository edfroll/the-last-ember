# generated: statue 54: the head turns after the player (the face along the way out)
setblock -141 114 -393 minecraft:polished_diorite_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n54 le.mz 0
scoreboard players set #h54 le.mz 1
scoreboard players operation #hr54 le.mz = #gt le.mz
scoreboard players add #hr54 le.mz 1200
