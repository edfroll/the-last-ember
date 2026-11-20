# T-026: the look of a player from his eyes to the head of a pool (tag le.fhtg), steps of 0.4: #seen 1 when the head is reached before a
# block that hides it (#last_ember:fens_gaze: air, water, plants, lily pads...); 24 blocks at most
scoreboard players add #rs le.fn 1
execute if score #rs le.fn matches 62.. run return run scoreboard players set #rs le.fn 0
execute positioned ~-0.5 ~-0.5 ~-0.5 if entity @e[type=minecraft:item_display,tag=le.fhtg,dx=0,dy=0,dz=0] run return run function last_ember:fens/seen
execute unless block ~ ~ ~ #last_ember:fens_gaze run return run scoreboard players set #rs le.fn 0
execute positioned ^ ^ ^0.4 run function last_ember:fens/look
