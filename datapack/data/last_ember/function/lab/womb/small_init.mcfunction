scoreboard players set @s le.ls 2
function last_ember:lab/init
execute store result entity @s Motion[0] double 0.01 run random value -30..30
execute store result entity @s Motion[2] double 0.01 run random value -30..30
data modify entity @s Motion[1] set value 0.45d
