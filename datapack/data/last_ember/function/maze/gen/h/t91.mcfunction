# generated: statue 91: the head turns after the player (the face along the way out)
setblock -107 114 -436 minecraft:tuff_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n91 le.mz 0
scoreboard players set #h91 le.mz 1
scoreboard players operation #hr91 le.mz = #gt le.mz
scoreboard players add #hr91 le.mz 1200
