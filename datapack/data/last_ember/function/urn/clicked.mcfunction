advancement revoke @s only last_ember:urn/click
tag @s add le.clicker
execute as @e[type=minecraft:interaction,tag=le.urnclick,distance=..10] if function last_ember:bonfire/is_mine at @s run function last_ember:urn/collect
tag @s remove le.clicker
