# generated: statue 63: the head turns after the player (the face along the way out)
setblock -117 114 -450 minecraft:tuff_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n63 le.mz 0
scoreboard players set #h63 le.mz 1
scoreboard players operation #hr63 le.mz = #gt le.mz
scoreboard players add #hr63 le.mz 1200
