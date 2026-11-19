# T-025: the look of the wearer, from his eyes to the target (le.ctg), steps of 0.4: #ok 2 when the target is reached before a solid block
scoreboard players add #rs le.gd 1
execute if score #rs le.gd matches 35.. run return 0
execute positioned ~-0.5 ~-0.5 ~-0.5 if entity @e[tag=le.ctg,dx=0,dy=0,dz=0] run return run scoreboard players set #ok le.gd 2
execute unless block ~ ~ ~ #last_ember:gaze_pass run return 0
execute positioned ^ ^ ^0.4 run function last_ember:creak/ray
