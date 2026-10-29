# positioned at a candidate point: 1 when a player within 64 looks toward it (less than 60 degrees off his look)
summon minecraft:marker ~ ~ ~ {Tags:["le.cpt"]}
scoreboard players set #seen le.ct 0
execute as @a[distance=..64,gamemode=!spectator] at @s run function last_ember:contract/seen_p
kill @e[type=minecraft:marker,tag=le.cpt]
return run scoreboard players get #seen le.ct
