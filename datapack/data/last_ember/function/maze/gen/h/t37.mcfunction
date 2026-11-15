# generated: statue 37: the head turns after the player (the face along the way out)
setblock -165 114 -400 minecraft:polished_diorite_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n37 le.mz 0
scoreboard players set #h37 le.mz 1
scoreboard players operation #hr37 le.mz = #gt le.mz
scoreboard players add #hr37 le.mz 1200
