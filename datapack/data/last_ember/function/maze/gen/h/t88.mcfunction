# generated: statue 88: the head turns after the player (the face along the way out)
setblock -93 114 -429 minecraft:polished_diorite_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n88 le.mz 0
scoreboard players set #h88 le.mz 1
scoreboard players operation #hr88 le.mz = #gt le.mz
scoreboard players add #hr88 le.mz 1200
