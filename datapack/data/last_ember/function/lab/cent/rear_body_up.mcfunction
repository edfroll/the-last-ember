# the first three segments stand up in an arc under the lifted head (the rest stays on the path)
execute rotated ~ 0 positioned ^ ^2.5 ^-1.2 as @e[type=minecraft:item_display,tag=le.cs0] if score @s le.lnk = #id le.l run tp @s ~ ~ ~ ~ -80
execute rotated ~ 0 positioned ^ ^1.4 ^-1.4 as @e[type=minecraft:item_display,tag=le.cs1] if score @s le.lnk = #id le.l run tp @s ~ ~ ~ ~ -75
execute rotated ~ 0 positioned ^ ^0.4 ^-1.9 as @e[type=minecraft:item_display,tag=le.cs2] if score @s le.lnk = #id le.l run tp @s ~ ~ ~ ~ -45
execute rotated ~ 0 positioned ^ ^0 ^-2.8 as @e[type=minecraft:item_display,tag=le.cs3] if score @s le.lnk = #id le.l run tp @s ~ ~ ~ ~ -12
