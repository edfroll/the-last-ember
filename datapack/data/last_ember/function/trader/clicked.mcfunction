# advancement reward: a player right-clicked a trader (the trade window opens as usual): the greeting once per player
advancement revoke @s only last_ember:trader/click
tag @s add le.clicker
execute as @e[type=#last_ember:traders,tag=le.trader,distance=..6,sort=nearest,limit=1] at @s run function last_ember:trader/gen/hello
tag @s remove le.clicker
