# generated: statue 15: the head turns after the player (the face along the way out)
setblock -165 114 -474 minecraft:tuff_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n15 le.mz 0
scoreboard players set #h15 le.mz 1
scoreboard players operation #hr15 le.mz = #gt le.mz
scoreboard players add #hr15 le.mz 1200
