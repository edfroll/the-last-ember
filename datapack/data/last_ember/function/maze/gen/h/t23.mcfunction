# generated: statue 23: the head turns after the player (the face along the way out)
setblock -170 114 -465 minecraft:tuff_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n23 le.mz 0
scoreboard players set #h23 le.mz 1
scoreboard players operation #hr23 le.mz = #gt le.mz
scoreboard players add #hr23 le.mz 1200
