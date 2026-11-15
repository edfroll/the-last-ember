# generated: statue 59: the head turns after the player (the face along the way out)
setblock -117 114 -465 minecraft:tuff_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n59 le.mz 0
scoreboard players set #h59 le.mz 1
scoreboard players operation #hr59 le.mz = #gt le.mz
scoreboard players add #hr59 le.mz 1200
