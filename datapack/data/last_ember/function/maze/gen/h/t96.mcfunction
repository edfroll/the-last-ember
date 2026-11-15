# generated: statue 96: the head turns after the player (the face along the way out)
setblock -113 114 -372 minecraft:tuff_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n96 le.mz 0
scoreboard players set #h96 le.mz 1
scoreboard players operation #hr96 le.mz = #gt le.mz
scoreboard players add #hr96 le.mz 1200
