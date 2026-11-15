# generated: statue 56: the head turns after the player (the face along the way out)
setblock -121 114 -472 minecraft:tuff_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n56 le.mz 0
scoreboard players set #h56 le.mz 1
scoreboard players operation #hr56 le.mz = #gt le.mz
scoreboard players add #hr56 le.mz 1200
