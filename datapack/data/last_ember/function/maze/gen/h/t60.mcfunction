# generated: statue 60: the head turns after the player (the face along the way out)
setblock -131 114 -465 minecraft:tuff_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n60 le.mz 0
scoreboard players set #h60 le.mz 1
scoreboard players operation #hr60 le.mz = #gt le.mz
scoreboard players add #hr60 le.mz 1200
