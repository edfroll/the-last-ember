# as a hit box: 1 when it belongs to segment #k
execute if score #k le.l matches 0 if entity @s[tag=le.cb0] run return 1
execute if score #k le.l matches 1 if entity @s[tag=le.cb1] run return 1
execute if score #k le.l matches 2 if entity @s[tag=le.cb2] run return 1
execute if score #k le.l matches 3 if entity @s[tag=le.cb3] run return 1
execute if score #k le.l matches 4 if entity @s[tag=le.cb4] run return 1
execute if score #k le.l matches 5 if entity @s[tag=le.cb5] run return 1
execute if score #k le.l matches 6 if entity @s[tag=le.cb6] run return 1
execute if score #k le.l matches 7 if entity @s[tag=le.cb7] run return 1
execute if score #k le.l matches 8 if entity @s[tag=le.cb8] run return 1
execute if score #k le.l matches 9 if entity @s[tag=le.cb9] run return 1
return 0
