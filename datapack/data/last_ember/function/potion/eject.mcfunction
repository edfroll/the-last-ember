# as an item entity: out of the cauldron, towards whoever threw it
tag @s add le.ej
execute on origin at @s run tp @e[type=minecraft:item,tag=le.ej,limit=1,distance=..8] ~ ~1.3 ~
tag @s remove le.ej
data modify entity @s PickupDelay set value 20s
