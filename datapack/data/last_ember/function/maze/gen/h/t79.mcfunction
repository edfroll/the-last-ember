# generated: statue 79: the head turns after the player (the face along the way out)
setblock -109 114 -455 minecraft:tuff_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n79 le.mz 0
scoreboard players set #h79 le.mz 1
scoreboard players operation #hr79 le.mz = #gt le.mz
scoreboard players add #hr79 le.mz 1200
