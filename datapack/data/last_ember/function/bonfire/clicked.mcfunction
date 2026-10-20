# advancement reward: a player right-clicked a bonfire interaction (hearth or stela)
advancement revoke @s only last_ember:bonfire/click
tag @s add le.clicker
execute as @e[type=minecraft:interaction,tag=le.bonfire,distance=..8] if function last_ember:bonfire/is_mine at @s run function last_ember:bonfire/on_click
tag @s remove le.clicker
