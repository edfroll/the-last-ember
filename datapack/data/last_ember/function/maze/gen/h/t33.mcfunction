# generated: statue 33: the head turns after the player (the face along the way out)
setblock -164 114 -397 minecraft:tuff_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n33 le.mz 0
scoreboard players set #h33 le.mz 1
scoreboard players operation #hr33 le.mz = #gt le.mz
scoreboard players add #hr33 le.mz 1200
