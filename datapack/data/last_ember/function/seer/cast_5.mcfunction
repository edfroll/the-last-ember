# as a seer: the spell 5 (cooldown 20 s, kept on the player)
execute if score #gt le.e < @s le.cd5 run return run function last_ember:seer/cd_msg {n:5}
execute store result score #ok le.e run function last_ember:seer/do_5
execute unless score #ok le.e matches 1 run return 0
scoreboard players operation @s le.cd5 = #gt le.e
scoreboard players add @s le.cd5 400
function last_ember:seer/hint
