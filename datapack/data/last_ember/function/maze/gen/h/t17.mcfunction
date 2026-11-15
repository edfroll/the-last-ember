# generated: statue 17: the head turns after the player (the face along the way out)
setblock -175 114 -459 minecraft:tuff_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n17 le.mz 0
scoreboard players set #h17 le.mz 1
scoreboard players operation #hr17 le.mz = #gt le.mz
scoreboard players add #hr17 le.mz 1200
