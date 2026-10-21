# as a ranger who fed / tried to mount a tameable animal: it is tamed at once (the owner is the ranger)
advancement revoke @s only last_ember:ranger/tame_horse
execute unless entity @s[tag=le.class.ranger] run return 0
tag @s add le.rtame
execute as @e[type=#last_ember:rideable,distance=..5,sort=nearest,limit=1] unless data entity @s {Tame:1b} run function last_ember:ranger/tame_horse_do
tag @s remove le.rtame
