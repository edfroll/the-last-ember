# generated: statue 19: the head turns after the player (the face along the way out)
setblock -164 114 -460 minecraft:tuff_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n19 le.mz 0
scoreboard players set #h19 le.mz 1
scoreboard players operation #hr19 le.mz = #gt le.mz
scoreboard players add #hr19 le.mz 1200
