# generated: statue 4: the head turns after the player (the face along the way out)
setblock -209 114 -429 minecraft:tuff_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n4 le.mz 0
scoreboard players set #h4 le.mz 1
scoreboard players operation #hr4 le.mz = #gt le.mz
scoreboard players add #hr4 le.mz 1200
