# as a player with the antidote (every tick)
execute if score #gt le.e > @s le.immune run return run tag @s remove le.immune
effect clear @s minecraft:poison
effect clear @s minecraft:wither
