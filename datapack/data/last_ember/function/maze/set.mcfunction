# ADMIN/TEST: function last_ember:maze/set {cell:1,var:2}: the movable cell (1..6 = (1,1) (3,1) (1,3) (3,3) (0,2) (4,2)) to its variant
# 1..3 now (placed even when somebody is inside; mobs on the new hedge are moved to the path)
$scoreboard players set #cell le.mz $(cell)
$scoreboard players set #var le.mz $(var)
scoreboard players set #pv1 le.mz 0
scoreboard players set #pv2 le.mz 0
scoreboard players set #pv3 le.mz 0
scoreboard players set #pv4 le.mz 0
scoreboard players set #pv5 le.mz 0
scoreboard players set #pv6 le.mz 0
execute in minecraft:overworld run function last_ember:maze/gen/set
