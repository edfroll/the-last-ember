# macro e: the eye height; as the ray marker at the last free point: the cell of the feet (block centre), else back along the ray; 1 = teleported
$execute positioned ~ ~-$(e) ~ align xyz positioned ~0.5 ~ ~0.5 store result score #ok le.e run function last_ember:seer/blink_check
execute if score #ok le.e matches 1 run return 1
scoreboard players remove #k le.e 1
execute unless score #k le.e matches 1.. run return 0
tp @s ^ ^ ^-0.5
execute at @s run return run function last_ember:seer/blink_land with storage last_ember:seer c
