# generated: statue 51: the head turns after the player (the face along the way out)
setblock -161 114 -377 minecraft:tuff_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n51 le.mz 0
scoreboard players set #h51 le.mz 1
scoreboard players operation #hr51 le.mz = #gt le.mz
scoreboard players add #hr51 le.mz 1200
