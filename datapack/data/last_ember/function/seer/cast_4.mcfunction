# as a seer: the spell 4 (cooldown 25 s, kept on the player)
execute if score #gt le.e < @s le.cd4 run return run function last_ember:seer/cd_msg {n:4}
execute store result score #ok le.e run function last_ember:seer/do_4
execute unless score #ok le.e matches 1 run return 0
scoreboard players operation @s le.cd4 = #gt le.e
scoreboard players add @s le.cd4 500
function last_ember:seer/hint
