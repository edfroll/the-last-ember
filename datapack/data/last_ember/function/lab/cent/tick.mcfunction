# as the carrier at itself, every tick: a new point of the path when it has moved 0.25 block (then the segments move); the legs step while it moves
scoreboard players operation #id le.l = @s le.lnk
tag @s add le.cme
execute as @e[type=minecraft:marker,tag=le.cmark] if score @s le.lnk = #id le.l at @s unless entity @e[tag=le.cme,distance=..0.25] run function last_ember:lab/cent/rec
tag @s remove le.cme
scoreboard players operation #t3 le.l = #gt le.l
scoreboard players operation #t3 le.l %= #3 le.l
execute if score #t3 le.l matches 0 if score @s le.lsp matches 2.. run function last_ember:lab/cent/step
# the feelers twitch (a new sway every 4 ticks, the left and the right one in turn); the claws chew, or open before a bite and snap
scoreboard players operation #t4 le.l = #gt le.l
scoreboard players operation #t4 le.l %= #4 le.l
execute if score #t4 le.l matches 0 run function last_ember:lab/gen/cent_ant_l
execute if score #t4 le.l matches 2 run function last_ember:lab/gen/cent_ant_r
execute if score @s le.lan matches 1.. run return run function last_ember:lab/cent/snap_tick
scoreboard players operation #t5 le.l = #gt le.l
scoreboard players operation #t5 le.l %= #5 le.l
execute if score #t5 le.l matches 0 run function last_ember:lab/gen/cent_claw_chew
