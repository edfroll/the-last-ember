# generated: statue 61: the head turns after the player (the face along the way out)
setblock -120 114 -465 minecraft:tuff_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n61 le.mz 0
scoreboard players set #h61 le.mz 1
scoreboard players operation #hr61 le.mz = #gt le.mz
scoreboard players add #hr61 le.mz 1200
