# as the path marker: it moves to the carrier and remembers the point (newest first, 42 points = ~10 blocks of path)
tp @s @e[tag=le.cme,limit=1]
data modify storage last_ember:lab cp set value {}
data modify storage last_ember:lab cp.x set from entity @s Pos[0]
data modify storage last_ember:lab cp.y set from entity @s Pos[1]
data modify storage last_ember:lab cp.z set from entity @s Pos[2]
data modify entity @s data.h prepend from storage last_ember:lab cp
data remove entity @s data.h[42]
data modify storage last_ember:lab ch set from entity @s data.h
function last_ember:lab/gen/cent_place
