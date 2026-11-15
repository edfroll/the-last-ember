# generated: statue 29: the head turns after the player (the face along the way out)
setblock -165 114 -420 minecraft:tuff_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n29 le.mz 0
scoreboard players set #h29 le.mz 1
scoreboard players operation #hr29 le.mz = #gt le.mz
scoreboard players add #hr29 le.mz 1200
