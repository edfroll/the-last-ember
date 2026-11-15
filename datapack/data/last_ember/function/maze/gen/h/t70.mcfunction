# generated: statue 70: the head turns after the player (the face along the way out)
setblock -116 114 -417 minecraft:tuff_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n70 le.mz 0
scoreboard players set #h70 le.mz 1
scoreboard players operation #hr70 le.mz = #gt le.mz
scoreboard players add #hr70 le.mz 1200
