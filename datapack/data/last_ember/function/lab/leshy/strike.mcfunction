# who stands in front of it within reach is hit (a shield blocks it: the source has a position)
tag @s add le.lme
execute rotated as @s positioned ^ ^ ^1.8 as @a[distance=..2.6,gamemode=!spectator,gamemode=!creative] at @s run function last_ember:lab/leshy/hit_player
tag @s remove le.lme
