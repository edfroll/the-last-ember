# generated: statue 77: the head turns after the player (the face along the way out)
setblock -97 114 -477 minecraft:tuff_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n77 le.mz 0
scoreboard players set #h77 le.mz 1
scoreboard players operation #hr77 le.mz = #gt le.mz
scoreboard players add #hr77 le.mz 1200
