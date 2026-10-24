# who is in front of its maw (up to ~3.8 blocks) is bitten and bleeds; a shield blocks it (the source has a position)
tag @s add le.lme
execute rotated as @s rotated ~ 0 positioned ^ ^ ^2.4 as @a[distance=..1.9,gamemode=!spectator,gamemode=!creative] at @s run function last_ember:lab/warg/bitten
tag @s remove le.lme
