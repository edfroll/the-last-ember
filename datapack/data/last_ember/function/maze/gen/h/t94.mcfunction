# generated: statue 94: the head turns after the player (the face along the way out)
setblock -113 114 -417 minecraft:tuff_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n94 le.mz 0
scoreboard players set #h94 le.mz 1
scoreboard players operation #hr94 le.mz = #gt le.mz
scoreboard players add #hr94 le.mz 1200
