# generated: statue 49: the head turns after the player (the face along the way out)
setblock -161 114 -417 minecraft:tuff_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n49 le.mz 0
scoreboard players set #h49 le.mz 1
scoreboard players operation #hr49 le.mz = #gt le.mz
scoreboard players add #hr49 le.mz 1200
