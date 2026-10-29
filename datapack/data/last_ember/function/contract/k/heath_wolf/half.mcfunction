# at half health it howls and runs faster
tag @s add le.crage
playsound last_ember:creature.wild_dog.howl hostile @a[distance=..64] ~ ~ ~ 2.6 0.85
attribute @s minecraft:movement_speed modifier add last_ember:ct_rage 0.35 add_multiplied_base
particle minecraft:large_smoke ~ ~1.5 ~ 0.5 0.4 0.5 0.03 30
$tag @s add le.half_$(id)
