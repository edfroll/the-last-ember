$execute if score @s le.sd matches 0 in minecraft:overworld run spawnpoint @s $(x) $(y) $(z)
$execute if score @s le.sd matches 1 in minecraft:the_nether run spawnpoint @s $(x) $(y) $(z)
$execute if score @s le.sd matches 2 in minecraft:the_end run spawnpoint @s $(x) $(y) $(z)
