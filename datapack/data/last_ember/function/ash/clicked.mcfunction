advancement revoke @s only last_ember:ash/click
tag @s add le.clicker
execute as @e[type=minecraft:interaction,tag=le.ashclick,distance=..8] if function last_ember:bonfire/is_mine at @s run function last_ember:ash/collect
tag @s remove le.clicker
