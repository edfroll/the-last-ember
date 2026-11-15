# generated: statue 28: the head turns after the player (the face along the way out)
setblock -180 114 -429 minecraft:tuff_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n28 le.mz 0
scoreboard players set #h28 le.mz 1
scoreboard players operation #hr28 le.mz = #gt le.mz
scoreboard players add #hr28 le.mz 1200
