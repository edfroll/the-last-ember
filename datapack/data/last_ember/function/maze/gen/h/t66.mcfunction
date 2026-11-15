# generated: statue 66: the head turns after the player (the face along the way out)
setblock -116 114 -465 minecraft:tuff_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n66 le.mz 0
scoreboard players set #h66 le.mz 1
scoreboard players operation #hr66 le.mz = #gt le.mz
scoreboard players add #hr66 le.mz 1200
