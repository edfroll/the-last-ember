# T-027: advancement reward: a player right-clicked the spyglass: at night 15 s of soul lights over the right graves for him only (the
# cooldown 20 s for him); by day a line
advancement revoke @s only last_ember:cemetery/spy
execute unless predicate last_ember:night run return run title @s actionbar {"text":"Днём туман молчит. Смотри ночью.","color":"gray","italic":true}
execute if score @s le.cspc > #gt le.cem run return 0
scoreboard players operation @s le.cspy = #gt le.cem
scoreboard players add @s le.cspy 300
scoreboard players operation @s le.cspc = #gt le.cem
scoreboard players add @s le.cspc 400
playsound minecraft:item.spyglass.use player @s ~ ~ ~ 1 0.8
