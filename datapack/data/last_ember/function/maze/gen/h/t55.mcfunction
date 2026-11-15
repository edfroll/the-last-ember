# generated: statue 55: the head turns after the player (the face along the way out)
setblock -122 114 -489 minecraft:tuff_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n55 le.mz 0
scoreboard players set #h55 le.mz 1
scoreboard players operation #hr55 le.mz = #gt le.mz
scoreboard players add #hr55 le.mz 1200
