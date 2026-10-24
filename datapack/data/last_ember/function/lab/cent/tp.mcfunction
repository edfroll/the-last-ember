# as a segment: to its point, facing the point ahead of it (level); its hit box comes along
$tp @s $(x) $(y) $(z) facing $(fx) $(y) $(fz)
scoreboard players operation #k le.l = @s le.lfr
execute at @s as @e[type=minecraft:interaction,tag=le.cbox] if score @s le.lnk = #id le.l if function last_ember:lab/cent/same_k run tp @s ~ ~ ~
