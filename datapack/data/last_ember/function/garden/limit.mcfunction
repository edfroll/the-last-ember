# T-025: no more than 6 creakings in the garden: while there are more, the oldest sensor creaking crumbles
function last_ember:garden/gen/creakings
execute if score #ncr le.gd matches ..6 run return 0
execute as @e[type=minecraft:creaking,tag=le.garden_cr,sort=arbitrary,limit=1] at @s run function last_ember:garden/crumble
function last_ember:garden/limit
