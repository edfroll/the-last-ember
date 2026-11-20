# T-027: macro yaw, d, kind: the spirit at that point when the ground there is solid and in the cemetery
$execute rotated $(yaw) 0 positioned ^ ^ ^$(d) positioned over motion_blocking_no_leaves unless block ~ ~-1 ~ minecraft:water unless block ~ ~-1 ~ #minecraft:leaves if block ~ ~ ~ #minecraft:air if block ~ ~1 ~ #minecraft:air run function last_ember:cemetery/place_here {kind:"$(kind)"}
