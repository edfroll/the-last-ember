# generated: statue 1: the head turns after the player (the face along the way out)
setblock -197 114 -489 minecraft:tuff_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n1 le.mz 0
scoreboard players set #h1 le.mz 1
scoreboard players operation #hr1 le.mz = #gt le.mz
scoreboard players add #hr1 le.mz 1200
