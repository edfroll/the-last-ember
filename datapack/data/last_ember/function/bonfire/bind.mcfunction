# as a player: respawn point = respawn pad of storage last_ember:bt cur
execute store result score @s le.sx run data get storage last_ember:bt cur.rx
execute store result score @s le.sy run data get storage last_ember:bt cur.ry
execute store result score @s le.sz run data get storage last_ember:bt cur.rz
execute store result score @s le.sd run data get storage last_ember:bt cur.d
execute store result score @s le.sb run data get storage last_ember:bt cur.i
function last_ember:bonfire/apply_spawn
