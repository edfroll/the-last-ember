# T-022: a chorus fruit is eaten (the advancement fires before the random teleport): remember where; gate/loop checks the next 6 ticks (the hop may land a tick later)
advancement revoke @s only last_ember:gate/chorus
execute store result score @s le.chx run data get entity @s Pos[0] 10
execute store result score @s le.chy run data get entity @s Pos[1] 10
execute store result score @s le.chz run data get entity @s Pos[2] 10
tag @s add le.chorus
# T-024: zones with the flag no_chorus (the maze): the hop is undone (gate/chorus_zone); the previous position for the hop test
scoreboard players operation @s le.cpx = @s le.chx
scoreboard players operation @s le.cpy = @s le.chy
scoreboard players operation @s le.cpz = @s le.chz
tag @s remove le.chz
execute if entity @s[tag=le.zf.no_chorus] run tag @s add le.chz
scoreboard players set @s le.cht 6
