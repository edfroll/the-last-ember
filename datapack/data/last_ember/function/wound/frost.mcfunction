# MODULE (as a player): Frost (Стужа, T-020) — slowness I and mining fatigue I for 6 s, snowflakes; the Warmth of the Ember (tag le.warm) lifts it at once
execute if entity @s[tag=le.warm] run return run title @s actionbar {"text":"Тепло Угля отгоняет стужу","color":"gold"}
tag @s add le.wound
effect give @s minecraft:slowness 6 0 true
effect give @s minecraft:mining_fatigue 6 0 true
scoreboard players set @s le.wfr 120
title @s actionbar {"text":"Стужа сковывает руки","color":"aqua"}
playsound minecraft:block.powder_snow.step player @s ~ ~ ~ 1 0.6
