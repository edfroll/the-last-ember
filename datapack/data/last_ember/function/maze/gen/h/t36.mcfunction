# generated: statue 36: the head turns after the player (the face along the way out)
setblock -164 114 -417 minecraft:polished_diorite_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n36 le.mz 0
scoreboard players set #h36 le.mz 1
scoreboard players operation #hr36 le.mz = #gt le.mz
scoreboard players add #hr36 le.mz 1200
