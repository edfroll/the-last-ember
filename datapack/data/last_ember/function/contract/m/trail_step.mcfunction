# the blood trail of a drag: a marker every 3 blocks toward the target marker (le.ctarget), at most 30
summon minecraft:marker ~ ~ ~ {Tags:["le.ctrail","le.ctrail_new"]}
scoreboard players add #steps le.ct 1
execute if score #steps le.ct matches 30.. run return 0
execute positioned ^ ^ ^3 unless entity @e[type=minecraft:marker,tag=le.ctarget,distance=..3] run function last_ember:contract/m/trail_step
