# generated: statue 12: the head turns after the player (the face along the way out)
setblock -192 114 -377 minecraft:tuff_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n12 le.mz 0
scoreboard players set #h12 le.mz 1
scoreboard players operation #hr12 le.mz = #gt le.mz
scoreboard players add #hr12 le.mz 1200
