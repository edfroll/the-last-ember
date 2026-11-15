# generated: statue 81: the head turns after the player (the face along the way out)
setblock -108 114 -429 minecraft:tuff_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n81 le.mz 0
scoreboard players set #h81 le.mz 1
scoreboard players operation #hr81 le.mz = #gt le.mz
scoreboard players add #hr81 le.mz 1200
