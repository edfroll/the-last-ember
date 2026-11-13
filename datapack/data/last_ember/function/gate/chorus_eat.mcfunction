# T-022: a chorus fruit is eaten (the advancement fires before the random teleport): remember where; gate/loop checks the next tick
advancement revoke @s only last_ember:gate/chorus
execute store result score @s le.chx run data get entity @s Pos[0] 10
execute store result score @s le.chy run data get entity @s Pos[1] 10
execute store result score @s le.chz run data get entity @s Pos[2] 10
tag @s add le.chorus
