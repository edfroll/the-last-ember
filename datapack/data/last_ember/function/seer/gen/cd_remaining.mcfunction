# as a seer: #r le.e = seconds left of the spell #sel (0 = ready)
scoreboard players set #r le.e 0
execute if score #sel le.e matches 1 run scoreboard players operation #r le.e = @s le.cd1
execute if score #sel le.e matches 2 run scoreboard players operation #r le.e = @s le.cd2
execute if score #sel le.e matches 3 run scoreboard players operation #r le.e = @s le.cd3
execute if score #sel le.e matches 4 run scoreboard players operation #r le.e = @s le.cd4
execute if score #sel le.e matches 5 run scoreboard players operation #r le.e = @s le.cd5
execute if score #sel le.e matches 6 run scoreboard players operation #r le.e = @s le.cd6
execute if score #sel le.e matches 7 run scoreboard players operation #r le.e = @s le.cd7
scoreboard players operation #r le.e -= #gt le.e
execute if score #r le.e matches ..0 run return run scoreboard players set #r le.e 0
scoreboard players add #r le.e 19
scoreboard players operation #r le.e /= #20 le.e
