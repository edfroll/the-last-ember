# as a player whose transfer is cancelled (left the trigger) or done: the state is cleared
tag @s remove le.sct
scoreboard players reset @s le.sct
scoreboard players set @s le.scw 0
execute if entity @s[gamemode=!spectator,gamemode=!creative] run effect clear @s minecraft:darkness
execute if entity @s[gamemode=!spectator,gamemode=!creative] run effect clear @s minecraft:blindness
