# as the cauldron: a whole recipe in the water -> brewing for 30 s (recipes need the mushroom base for 10 s first; not those of potion/nobase, T-026)
function last_ember:potion/match
execute if score @s le.crec matches 0 run return 0
execute if score @s le.crec matches 1..99 unless score @s le.cbase matches 200.. unless function last_ember:potion/nobase run return 0
execute unless block ~ ~ ~ minecraft:water_cauldron run return run title @a[distance=..6,tag=le.class.healer,limit=1] actionbar {"text":"Котлу нужна вода","color":"gray"}
scoreboard players set @s le.cstate 1
scoreboard players set @s le.ctimer 150
execute as @p[distance=..8,tag=le.class.healer] run scoreboard players operation #t le.e = @s le.tier
scoreboard players operation @s le.ctier = #t le.e
playsound minecraft:block.brewing_stand.brew block @a[distance=..12] ~ ~ ~ 1 1
