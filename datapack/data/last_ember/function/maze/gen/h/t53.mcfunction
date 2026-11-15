# generated: statue 53: the head turns after the player (the face along the way out)
setblock -145 114 -393 minecraft:polished_diorite_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n53 le.mz 0
scoreboard players set #h53 le.mz 1
scoreboard players operation #hr53 le.mz = #gt le.mz
scoreboard players add #hr53 le.mz 1200
