# the eyes face where the warg faces; in the bushes it watches the nearest player
execute if score @s le.ls matches ..1 facing entity @p[distance=..24] feet on passengers run rotate @s ~ 0
execute if score @s le.ls matches 2.. run function last_ember:lab/turn
