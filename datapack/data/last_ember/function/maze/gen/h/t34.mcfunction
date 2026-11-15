# generated: statue 34: the head turns after the player (the face along the way out)
setblock -181 114 -407 minecraft:tuff_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n34 le.mz 0
scoreboard players set #h34 le.mz 1
scoreboard players operation #hr34 le.mz = #gt le.mz
scoreboard players add #hr34 le.mz 1200
