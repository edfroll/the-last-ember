# as a seer: the spell 6 (cooldown 12 s, kept on the player)
execute if score #gt le.e < @s le.cd6 run return run function last_ember:seer/cd_msg {n:6}
execute store result score #ok le.e run function last_ember:seer/do_6
execute unless score #ok le.e matches 1 run return 0
scoreboard players operation @s le.cd6 = #gt le.e
scoreboard players add @s le.cd6 240
function last_ember:seer/hint
