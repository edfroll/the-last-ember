# generated: statue 43: the head turns after the player (the face along the way out)
setblock -165 114 -393 minecraft:polished_diorite_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n43 le.mz 0
scoreboard players set #h43 le.mz 1
scoreboard players operation #hr43 le.mz = #gt le.mz
scoreboard players add #hr43 le.mz 1200
