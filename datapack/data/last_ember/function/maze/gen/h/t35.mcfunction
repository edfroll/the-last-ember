# generated: statue 35: the head turns after the player (the face along the way out)
setblock -170 114 -412 minecraft:tuff_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n35 le.mz 0
scoreboard players set #h35 le.mz 1
scoreboard players operation #hr35 le.mz = #gt le.mz
scoreboard players add #hr35 le.mz 1200
