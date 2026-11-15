# generated: statue 24: the head turns after the player (the face along the way out)
setblock -165 114 -444 minecraft:polished_diorite_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n24 le.mz 0
scoreboard players set #h24 le.mz 1
scoreboard players operation #hr24 le.mz = #gt le.mz
scoreboard players add #hr24 le.mz 1200
