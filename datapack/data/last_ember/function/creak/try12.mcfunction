# T-025: as a monster near the wearer (le.cgz), nearest first: inside the cone of 25 degrees (2 sin(25/2) = 0.433) and seen (the ray) -> stilled
execute if score #cf le.gd matches 1 run return 0
tag @s add le.ctg
scoreboard players set #ok le.gd 0
execute as @a[tag=le.cgz,limit=1] at @s anchored eyes facing entity @e[tag=le.ctg,limit=1] eyes anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.433] run scoreboard players set #ok le.gd 1
scoreboard players set #rs le.gd 0
execute if score #ok le.gd matches 1 as @a[tag=le.cgz,limit=1] at @s anchored eyes facing entity @e[tag=le.ctg,limit=1] eyes positioned ^ ^ ^ run function last_ember:creak/ray
execute if score #ok le.gd matches 2 run function last_ember:creak/hit
tag @s remove le.ctg
