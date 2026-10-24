# the strike: the whole front of the body crashes down forward; who is in front of it within reach takes a heavy blow and is thrown up
function last_ember:lab/gen/cent_rear_slam
function last_ember:lab/gen/cent_claw_snap
execute rotated ~ 0 positioned ^ ^ ^0.4 as @e[type=minecraft:item_display,tag=le.cs0] if score @s le.lnk = #id le.l run tp @s ~ ~ ~ ~ 8
execute rotated ~ 0 positioned ^ ^ ^-0.7 as @e[type=minecraft:item_display,tag=le.cs1] if score @s le.lnk = #id le.l run tp @s ~ ~ ~ ~ 0
execute rotated ~ 0 positioned ^ ^ ^-1.8 as @e[type=minecraft:item_display,tag=le.cs2] if score @s le.lnk = #id le.l run tp @s ~ ~ ~ ~ 0
execute rotated ~ 0 positioned ^ ^ ^-2.9 as @e[type=minecraft:item_display,tag=le.cs3] if score @s le.lnk = #id le.l run tp @s ~ ~ ~ ~ 0
function last_ember:lab/s/fish_emerge
playsound last_ember:creature.scolopendromorph.combat_hit hostile @a ~ ~ ~ 1.8 0.8
execute rotated ~ 0 positioned ^ ^ ^1.8 run particle minecraft:block{block_state:"minecraft:coarse_dirt"} ~ ~0.2 ~ 1.0 0.3 1.0 0.25 50
tag @s add le.lme
execute rotated ~ 0 positioned ^ ^ ^2.4 as @a[distance=..2.5,gamemode=!spectator,gamemode=!creative] at @s run function last_ember:lab/cent/slam_hit
tag @s remove le.lme
