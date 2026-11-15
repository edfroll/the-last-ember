# generated: statue 76: the head turns after the player (the face along the way out)
setblock -128 114 -388 minecraft:tuff_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n76 le.mz 0
scoreboard players set #h76 le.mz 1
scoreboard players operation #hr76 le.mz = #gt le.mz
scoreboard players add #hr76 le.mz 1200
