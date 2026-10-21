# as a ranger who fed / tried to mount a tameable animal: it is tamed at once (the owner is the ranger)
advancement revoke @s only last_ember:ranger/tame_cat
execute unless entity @s[tag=le.class.ranger] run return 0
tag @s add le.rtame
execute as @e[type=minecraft:cat,distance=..5,sort=nearest,limit=1] unless data entity @s Owner run data modify entity @s Owner set from entity @a[tag=le.rtame,limit=1] UUID
tag @s remove le.rtame
