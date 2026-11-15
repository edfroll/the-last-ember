# generated: statue 18: the head turns after the player (the face along the way out)
setblock -164 114 -465 minecraft:tuff_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n18 le.mz 0
scoreboard players set #h18 le.mz 1
scoreboard players operation #hr18 le.mz = #gt le.mz
scoreboard players add #hr18 le.mz 1200
