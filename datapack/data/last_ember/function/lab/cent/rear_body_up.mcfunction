# the first three segments stand up in an arc under the lifted head (the rest stays on the path)
execute rotated ~ 0 positioned ^ ^1.3 ^-1.1 as @e[type=minecraft:item_display,tag=le.cs0] if score @s le.lnk = #id le.l run tp @s ~ ~ ~ ~ -70
execute rotated ~ 0 positioned ^ ^0.4 ^-1.6 as @e[type=minecraft:item_display,tag=le.cs1] if score @s le.lnk = #id le.l run tp @s ~ ~ ~ ~ -50
execute rotated ~ 0 positioned ^ ^0 ^-2.4 as @e[type=minecraft:item_display,tag=le.cs2] if score @s le.lnk = #id le.l run tp @s ~ ~ ~ ~ -15
