# generated: statue 31: the head turns after the player (the face along the way out)
setblock -179 114 -397 minecraft:tuff_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n31 le.mz 0
scoreboard players set #h31 le.mz 1
scoreboard players operation #hr31 le.mz = #gt le.mz
scoreboard players add #hr31 le.mz 1200
