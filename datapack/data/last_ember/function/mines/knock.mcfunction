# T-033: as resting Bran (every second): every 2..4 s his pickaxe on the vein, heard within 20 (volume 1.3: 16 x 1.3 blocks), through
# the big collapse; counted (tests)
scoreboard players remove @s le.mnt 1
execute if score @s le.mnt matches 1.. run return 0
execute store result score @s le.mnt run random value 2..4
execute at @s run playsound minecraft:block.stone.hit block @a[distance=..20] ~ ~1 ~ 1.3 0.75
scoreboard players add #knocks le.mn 1
