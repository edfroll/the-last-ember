# generated: statue 95: the head turns after the player (the face along the way out)
setblock -92 114 -417 minecraft:polished_diorite_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n95 le.mz 0
scoreboard players set #h95 le.mz 1
scoreboard players operation #hr95 le.mz = #gt le.mz
scoreboard players add #hr95 le.mz 1200
