# generated: statue 13: the head turns after the player (the face along the way out)
setblock -188 114 -393 minecraft:tuff_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n13 le.mz 0
scoreboard players set #h13 le.mz 1
scoreboard players operation #hr13 le.mz = #gt le.mz
scoreboard players add #hr13 le.mz 1200
