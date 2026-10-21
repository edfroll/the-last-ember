# as an ashborn every tick: no withering; under water the air runs out 3x faster (2 extra per tick on top of the vanilla 1)
effect clear @s minecraft:wither
execute at @s anchored eyes positioned ^ ^ ^ if block ~ ~ ~ minecraft:water run function last_ember:char/ash_air
