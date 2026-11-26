# T-033: as a resting dead miner (every second): every 3..6 s his pickaxe on the stone (block.stone.hit, heard within 16)
scoreboard players remove @s le.mnt 1
execute if score @s le.mnt matches 1.. run return 0
execute store result score @s le.mnt run random value 3..6
execute at @s run playsound minecraft:block.stone.hit block @a[distance=..16] ~ ~1 ~ 1 0.7
