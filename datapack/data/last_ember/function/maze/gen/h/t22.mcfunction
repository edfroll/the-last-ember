# generated: statue 22: the head turns after the player (the face along the way out)
setblock -181 114 -465 minecraft:tuff_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n22 le.mz 0
scoreboard players set #h22 le.mz 1
scoreboard players operation #hr22 le.mz = #gt le.mz
scoreboard players add #hr22 le.mz 1200
