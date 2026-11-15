# generated: statue 80: the head turns after the player (the face along the way out)
setblock -93 114 -444 minecraft:tuff_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n80 le.mz 0
scoreboard players set #h80 le.mz 1
scoreboard players operation #hr80 le.mz = #gt le.mz
scoreboard players add #hr80 le.mz 1200
