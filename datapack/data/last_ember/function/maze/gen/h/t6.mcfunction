# generated: statue 6: the head turns after the player (the face along the way out)
setblock -209 114 -441 minecraft:tuff_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n6 le.mz 0
scoreboard players set #h6 le.mz 1
scoreboard players operation #hr6 le.mz = #gt le.mz
scoreboard players add #hr6 le.mz 1200
