# generated: statue 85: the head turns after the player (the face along the way out)
setblock -113 114 -420 minecraft:tuff_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n85 le.mz 0
scoreboard players set #h85 le.mz 1
scoreboard players operation #hr85 le.mz = #gt le.mz
scoreboard players add #hr85 le.mz 1200
