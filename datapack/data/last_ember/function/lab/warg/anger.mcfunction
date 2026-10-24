execute unless entity @p[distance=..32,gamemode=!spectator,gamemode=!creative] run return 0
data modify entity @s angry_at set from entity @p[distance=..32,gamemode=!spectator,gamemode=!creative] UUID
execute store result entity @s anger_end_time long 1 run scoreboard players add #gt le.l 600
scoreboard players remove #gt le.l 600
