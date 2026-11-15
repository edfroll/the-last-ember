# generated: statue 14: the head turns after the player (the face along the way out)
setblock -164 114 -489 minecraft:tuff_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n14 le.mz 0
scoreboard players set #h14 le.mz 1
scoreboard players operation #hr14 le.mz = #gt le.mz
scoreboard players add #hr14 le.mz 1200
