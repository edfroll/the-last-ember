# generated: statue 46: the head turns after the player (the face along the way out)
setblock -161 114 -465 minecraft:tuff_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n46 le.mz 0
scoreboard players set #h46 le.mz 1
scoreboard players operation #hr46 le.mz = #gt le.mz
scoreboard players add #hr46 le.mz 1200
