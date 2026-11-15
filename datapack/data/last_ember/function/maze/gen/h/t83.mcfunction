# generated: statue 83: the head turns after the player (the face along the way out)
setblock -98 114 -421 minecraft:polished_diorite_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]
scoreboard players set #n83 le.mz 0
scoreboard players set #h83 le.mz 1
scoreboard players operation #hr83 le.mz = #gt le.mz
scoreboard players add #hr83 le.mz 1200
