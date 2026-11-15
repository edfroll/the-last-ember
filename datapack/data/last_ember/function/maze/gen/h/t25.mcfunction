# generated: statue 25: the head turns after the player (the face along the way out)
setblock -185 114 -465 minecraft:tuff_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n25 le.mz 0
scoreboard players set #h25 le.mz 1
scoreboard players operation #hr25 le.mz = #gt le.mz
scoreboard players add #hr25 le.mz 1200
