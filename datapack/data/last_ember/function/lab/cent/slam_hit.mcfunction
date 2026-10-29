# the blow of the whole body: heavy damage, the player is thrown back (a wind burst at the head) and a little up; slow falling after it, no fall damage
# the body is not the claws: no venom (lab/hit/cent skips a player tagged le.noven)
tag @s add le.noven
damage @s 9 minecraft:mob_attack by @e[tag=le.lme,limit=1]
tag @s remove le.noven
effect give @s minecraft:slow_falling 3 0 true
execute at @e[tag=le.lme,limit=1] rotated ~ 0 positioned ^ ^ ^0.6 run summon minecraft:wind_charge ~ ~0.2 ~ {Motion:[0.0d,-1.0d,0.0d]}
