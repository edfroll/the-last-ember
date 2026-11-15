# generated: statue 78: the head turns after the player (the face along the way out)
setblock -98 114 -469 minecraft:tuff_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n78 le.mz 0
scoreboard players set #h78 le.mz 1
scoreboard players operation #hr78 le.mz = #gt le.mz
scoreboard players add #hr78 le.mz 1200
