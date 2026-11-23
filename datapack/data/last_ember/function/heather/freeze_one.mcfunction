# T-031: as a zombie / zombie villager of the zone at the first stroke: frozen (NoAI), vanilla ones marked to be given back their AI
tag @s add le.hfrz
execute unless entity @s[tag=le.hz] run tag @s add le.hfv
data modify entity @s NoAI set value 1b
