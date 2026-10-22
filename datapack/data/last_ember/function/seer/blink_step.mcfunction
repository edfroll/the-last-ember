# as the ray marker: half a block ahead while the blocks are passable (tag blink_pass) and the steps last
execute unless score #n le.e matches 1.. run return 0
scoreboard players remove #n le.e 1
execute unless block ^ ^ ^0.5 #last_ember:blink_pass run return 0
tp @s ^ ^ ^0.5
execute at @s run function last_ember:seer/blink_step
