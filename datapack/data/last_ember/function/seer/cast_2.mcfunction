# as a seer: the spell 2 (cooldown 8 s, kept on the player)
execute if score #gt le.e < @s le.cd2 run return run function last_ember:seer/cd_msg {n:2}
execute store result score #ok le.e run function last_ember:seer/do_2
execute unless score #ok le.e matches 1 run return 0
scoreboard players operation @s le.cd2 = #gt le.e
scoreboard players add @s le.cd2 160
function last_ember:seer/hint
