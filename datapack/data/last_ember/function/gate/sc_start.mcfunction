# as a player who stepped into the transfer trigger (le.scw = code): darkness, steps and wind; the teleport after 1 s (sc_tick)
tag @s add le.sct
scoreboard players set @s le.sct 20
ride @s dismount
execute if entity @s[gamemode=!spectator,gamemode=!creative] run effect give @s minecraft:blindness 3 0 true
execute if entity @s[gamemode=!spectator,gamemode=!creative] run effect give @s minecraft:darkness 3 0 true
playsound minecraft:block.stone.step player @s ~ ~ ~ 0.6 0.7
playsound last_ember:sfx.amb.wind_mountain ambient @s ~ ~ ~ 0.6 1
