# generated: statue 48: the head turns after the player (the face along the way out)
setblock -141 114 -459 minecraft:tuff_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n48 le.mz 0
scoreboard players set #h48 le.mz 1
scoreboard players operation #hr48 le.mz = #gt le.mz
scoreboard players add #hr48 le.mz 1200
