# generated: statue 87: the head turns after the player (the face along the way out)
setblock -104 114 -431 minecraft:tuff_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n87 le.mz 0
scoreboard players set #h87 le.mz 1
scoreboard players operation #hr87 le.mz = #gt le.mz
scoreboard players add #hr87 le.mz 1200
