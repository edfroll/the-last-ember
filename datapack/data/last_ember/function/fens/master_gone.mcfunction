# T-026: nobody near: the Master goes back into the dark gap (removed without drops: 300 below and killed, as in T-018)
execute as @e[type=minecraft:drowned,tag=le.fmaster] at @s run tp @s ~ ~-300 ~
kill @e[type=minecraft:drowned,tag=le.fmaster]
scoreboard players set #ms le.fn 0
function last_ember:fens/save
