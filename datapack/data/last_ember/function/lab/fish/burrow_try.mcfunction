scoreboard players set @s le.lfd 40
execute if entity @a[distance=..6,gamemode=!spectator,gamemode=!creative] run return 0
execute unless entity @a[distance=..24,gamemode=!spectator,gamemode=!creative] run return 0
execute unless block ~ ~-0.5 ~ #last_ember:diggable run return 0
scoreboard players set @s le.ls 5
scoreboard players set @s le.lt 0
data merge entity @s {NoAI:1b,Invulnerable:1b}
playsound last_ember:creature.endrega.exp_digging hostile @a ~ ~ ~ 1.8 1
