# T-032: macro x1 y1 z1 x2 y2 z2: the box round a player inside the place (41 x 19 x 41 at most)
$fill $(x1) $(y1) $(z1) $(x2) $(y2) $(z2) minecraft:air replace #minecraft:fire
$fill $(x1) $(y1) $(z1) $(x2) $(y2) $(z2) minecraft:air replace minecraft:lava
$fill $(x1) $(y1) $(z1) $(x2) $(y2) $(z2) minecraft:air replace #minecraft:campfires[lit=true]
