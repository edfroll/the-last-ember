# advancement reward: a player right-clicked a pad or an altar
advancement revoke @s only last_ember:char/click
tag @s add le.clicker
execute as @e[type=minecraft:interaction,tag=le.cpad,distance=..8] if function last_ember:bonfire/is_mine run function last_ember:char/on_click
tag @s remove le.clicker
