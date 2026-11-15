# generated: statue 89: the head turns after the player (the face along the way out)
setblock -113 114 -441 minecraft:tuff_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n89 le.mz 0
scoreboard players set #h89 le.mz 1
scoreboard players operation #hr89 le.mz = #gt le.mz
scoreboard players add #hr89 le.mz 1200
