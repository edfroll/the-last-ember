# as a seer: the spell 1 (cooldown 40 s, kept on the player)
execute if score #gt le.e < @s le.cd1 run return run function last_ember:seer/cd_msg {n:1}
execute store result score #ok le.e run function last_ember:seer/do_1
execute unless score #ok le.e matches 1 run return 0
scoreboard players operation @s le.cd1 = #gt le.e
scoreboard players add @s le.cd1 800
function last_ember:seer/hint
