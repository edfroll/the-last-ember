# generated: statue 47: the head turns after the player (the face along the way out)
setblock -155 114 -445 minecraft:tuff_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n47 le.mz 0
scoreboard players set #h47 le.mz 1
scoreboard players operation #hr47 le.mz = #gt le.mz
scoreboard players add #hr47 le.mz 1200
