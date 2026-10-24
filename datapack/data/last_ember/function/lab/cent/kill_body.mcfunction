# as the carrier: its segments, hit boxes and path marker go
scoreboard players operation #id le.l = @s le.lnk
execute as @e[tag=le.cseg] if score @s le.lnk = #id le.l run kill @s
execute as @e[type=minecraft:interaction,tag=le.cbox] if score @s le.lnk = #id le.l run kill @s
execute as @e[type=minecraft:marker,tag=le.cmark] if score @s le.lnk = #id le.l run kill @s
