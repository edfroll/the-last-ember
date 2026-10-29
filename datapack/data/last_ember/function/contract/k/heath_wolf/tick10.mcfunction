# every 10 ticks
function last_ember:contract/m/tick10
execute if entity @s[tag=le.crage] run particle minecraft:large_smoke ~ ~1.2 ~ 0.4 0.3 0.4 0.01 2
