$execute unless data storage last_ember:ash t.t$(id) run return 0
$data modify storage last_ember:dt rec set from storage last_ember:ash t.t$(id)
$data remove storage last_ember:ash t.t$(id)
data remove storage last_ember:dt bowl
execute as @a[tag=le.clicker,limit=1] at @s run function last_ember:ash/give_rec
schedule function last_ember:ash/out_to_bowl 3t replace
playsound minecraft:block.sand.break player @a[distance=..16] ~ ~ ~ 1 0.6
particle minecraft:white_ash ~ ~0.5 ~ 0.3 0.3 0.3 0.01 40
