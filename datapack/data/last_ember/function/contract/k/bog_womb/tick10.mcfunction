# in the water it is at home (armour, it heals); on dry land it weakens (half the blow, no armour) and dries out
function last_ember:contract/m/tick10
execute unless score @s le.ls matches 2 run return 0
scoreboard players set #wet le.ct 0
execute if block ~ ~0.3 ~ minecraft:water run scoreboard players set #wet le.ct 1
execute if block ~ ~-0.3 ~ minecraft:water run scoreboard players set #wet le.ct 1
execute if score #wet le.ct matches 1 if entity @s[tag=le.cdry] run function last_ember:contract/k/bog_womb/wet
execute if score #wet le.ct matches 1 run effect give @s minecraft:regeneration 1 1 true
execute if score #wet le.ct matches 0 if entity @s[tag=!le.cdry] run function last_ember:contract/k/bog_womb/dry
execute if score #wet le.ct matches 0 run particle minecraft:falling_dust{block_state:"minecraft:mud"} ~ ~1 ~ 0.8 0.4 0.8 0 4
