# generated: statue 93: the head turns after the player (the face along the way out)
setblock -107 114 -425 minecraft:tuff_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n93 le.mz 0
scoreboard players set #h93 le.mz 1
scoreboard players operation #hr93 le.mz = #gt le.mz
scoreboard players add #hr93 le.mz 1200
