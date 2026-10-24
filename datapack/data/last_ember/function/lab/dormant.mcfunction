# the row: the sample waits hidden until someone (not a spectator, not in creative) comes within 9 blocks
execute if entity @s[tag=le.lab_warg] run function last_ember:lab/warg/turn
execute if entity @a[distance=..9,gamemode=!spectator,gamemode=!creative] run scoreboard players set @s le.ls 1
