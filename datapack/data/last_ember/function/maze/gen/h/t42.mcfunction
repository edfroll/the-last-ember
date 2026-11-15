# generated: statue 42: the head turns after the player (the face along the way out)
setblock -165 114 -396 minecraft:tuff_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n42 le.mz 0
scoreboard players set #h42 le.mz 1
scoreboard players operation #hr42 le.mz = #gt le.mz
scoreboard players add #hr42 le.mz 1200
