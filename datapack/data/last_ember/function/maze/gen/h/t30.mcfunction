# generated: statue 30: the head turns after the player (the face along the way out)
setblock -185 114 -411 minecraft:tuff_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n30 le.mz 0
scoreboard players set #h30 le.mz 1
scoreboard players operation #hr30 le.mz = #gt le.mz
scoreboard players add #hr30 le.mz 1200
