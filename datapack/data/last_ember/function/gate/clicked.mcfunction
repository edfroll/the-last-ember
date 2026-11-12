# advancement reward: a player right-clicked the interaction of a shortcut (locked gate on the plaza or a region door)
advancement revoke @s only last_ember:gate/click
tag @s add le.scclicker
execute as @e[type=minecraft:interaction,tag=le.scclick,distance=..10] if function last_ember:gate/is_mine run function last_ember:gate/gen/click
tag @s remove le.scclicker
