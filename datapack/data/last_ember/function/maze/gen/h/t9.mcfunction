# generated: statue 9: the head turns after the player (the face along the way out)
setblock -194 114 -441 minecraft:tuff_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n9 le.mz 0
scoreboard players set #h9 le.mz 1
scoreboard players operation #hr9 le.mz = #gt le.mz
scoreboard players add #hr9 le.mz 1200
