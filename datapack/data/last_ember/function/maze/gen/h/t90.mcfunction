# generated: statue 90: the head turns after the player (the face along the way out)
setblock -113 114 -421 minecraft:tuff_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n90 le.mz 0
scoreboard players set #h90 le.mz 1
scoreboard players operation #hr90 le.mz = #gt le.mz
scoreboard players add #hr90 le.mz 1200
