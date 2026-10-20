# as a player: re-applies the bonfire respawn point (beds, anchors and /spawnpoint by others cannot replace it)
execute store result storage last_ember:bt sp.x int 1 run scoreboard players get @s le.sx
execute store result storage last_ember:bt sp.y int 1 run scoreboard players get @s le.sy
execute store result storage last_ember:bt sp.z int 1 run scoreboard players get @s le.sz
function last_ember:bonfire/apply_spawn_m with storage last_ember:bt sp
