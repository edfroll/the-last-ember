effect give @s minecraft:regeneration 6 1 true
effect give @s minecraft:strength 6 0 true
playsound minecraft:entity.player.breath player @a[distance=..16] ~ ~ ~ 1 0.9
scoreboard players operation @s le.swcd = #gt le.e
scoreboard players add @s le.swcd 3600
