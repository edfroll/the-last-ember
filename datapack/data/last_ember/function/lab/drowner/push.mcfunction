# as the drowner: Motion toward the nearest player, macro f = blocks per tick along the ground, y = up
$execute facing entity @p[gamemode=!spectator,gamemode=!creative] feet positioned 0.0 0.0 0.0 rotated ~ 0 positioned ^ ^ ^$(f) run summon minecraft:marker ~ ~ ~ {Tags:["le.lvec"]}
data modify entity @s Motion set from entity @e[type=minecraft:marker,tag=le.lvec,limit=1] Pos
$data modify entity @s Motion[1] set value $(y)d
kill @e[type=minecraft:marker,tag=le.lvec]
