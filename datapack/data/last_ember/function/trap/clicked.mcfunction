# advancement reward: a player right-clicked the false treasure
advancement revoke @s only last_ember:trap/click
tag @s add le.clicker
execute as @e[type=minecraft:interaction,tag=le.ft,distance=..8] if function last_ember:bonfire/is_mine at @s run function last_ember:trap/gen/ftc
tag @s remove le.clicker
