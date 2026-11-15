# generated: statue 21: the head turns after the player (the face along the way out)
setblock -185 114 -450 minecraft:tuff_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n21 le.mz 0
scoreboard players set #h21 le.mz 1
scoreboard players operation #hr21 le.mz = #gt le.mz
scoreboard players add #hr21 le.mz 1200
