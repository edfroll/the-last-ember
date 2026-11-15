# generated: statue 68: the head turns after the player (the face along the way out)
setblock -117 114 -420 minecraft:polished_diorite_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n68 le.mz 0
scoreboard players set #h68 le.mz 1
scoreboard players operation #hr68 le.mz = #gt le.mz
scoreboard players add #hr68 le.mz 1200
