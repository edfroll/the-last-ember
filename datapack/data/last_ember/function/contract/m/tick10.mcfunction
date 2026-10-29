# as the monster of a contract, every 10 ticks: the weakness runs out; fire hurts it more
execute if entity @s[tag=le.cweak] run scoreboard players remove @s le.cwk 10
execute if entity @s[tag=le.cweak] if score @s le.cwk matches ..0 run function last_ember:contract/m/unweak
execute if predicate last_ember:contract/on_fire run damage @s 2 minecraft:on_fire
