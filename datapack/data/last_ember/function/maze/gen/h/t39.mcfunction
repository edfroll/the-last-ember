# generated: statue 39: the head turns after the player (the face along the way out)
setblock -185 114 -417 minecraft:polished_diorite_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n39 le.mz 0
scoreboard players set #h39 le.mz 1
scoreboard players operation #hr39 le.mz = #gt le.mz
scoreboard players add #hr39 le.mz 1200
