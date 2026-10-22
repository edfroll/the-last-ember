# advancement reward: a player right-clicked a pedestal
advancement revoke @s only last_ember:altar/click
tag @s add le.clicker
execute as @e[type=minecraft:interaction,tag=le.ped,distance=..8] if function last_ember:bonfire/is_mine at @s run function last_ember:altar/ped_click
tag @s remove le.clicker
