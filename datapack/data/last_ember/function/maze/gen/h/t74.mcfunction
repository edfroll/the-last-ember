# generated: statue 74: the head turns after the player (the face along the way out)
setblock -117 114 -411 minecraft:polished_diorite_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n74 le.mz 0
scoreboard players set #h74 le.mz 1
scoreboard players operation #hr74 le.mz = #gt le.mz
scoreboard players add #hr74 le.mz 1200
