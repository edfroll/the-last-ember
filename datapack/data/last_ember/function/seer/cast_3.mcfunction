# as a seer: the spell 3 (cooldown 20 s, kept on the player)
execute if score #gt le.e < @s le.cd3 run return run function last_ember:seer/cd_msg {n:3}
execute store result score #ok le.e run function last_ember:seer/do_3
execute unless score #ok le.e matches 1 run return 0
scoreboard players operation @s le.cd3 = #gt le.e
scoreboard players add @s le.cd3 400
function last_ember:seer/hint
