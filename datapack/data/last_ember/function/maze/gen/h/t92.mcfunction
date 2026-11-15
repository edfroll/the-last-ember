# generated: statue 92: the head turns after the player (the face along the way out)
setblock -109 114 -431 minecraft:tuff_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n92 le.mz 0
scoreboard players set #h92 le.mz 1
scoreboard players operation #hr92 le.mz = #gt le.mz
scoreboard players add #hr92 le.mz 1200
