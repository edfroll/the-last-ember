# T-027: every 5 ticks: the buttons of the keeper's windows; every 10 ticks the souls of the spyglass and the Magister's weapon; every
# second the rest (cemetery/second)
schedule function last_ember:cemetery/loop 5t replace
execute store result score #gt le.cem run time query gametime
scoreboard players add #t le.cem 5
execute as @a[scores={le.ctrig=1..}] at @s run function last_ember:cemetery/trig
scoreboard players operation #t10 le.cem = #t le.cem
scoreboard players operation #t10 le.cem %= #10 le.cem
execute if score #t10 le.cem matches 0 as @a if score @s le.cspy > #gt le.cem in minecraft:overworld run function last_ember:cemetery/gen/spy
execute if score #t10 le.cem matches 0 if score #mg le.cem matches 1 in minecraft:overworld as @e[type=minecraft:skeleton,tag=le.cmag,limit=1] at @s run function last_ember:cemetery/mag_tick
scoreboard players operation #t20 le.cem = #t le.cem
scoreboard players operation #t20 le.cem %= #20 le.cem
execute if score #t20 le.cem matches 0 in minecraft:overworld run function last_ember:cemetery/second
