# as a hit box punched by a player: the blow goes to the carrier, counted like a vanilla blow of that player (T-020, remark 1 of the T-018 review):
# the weapon damage, Sharpness / Bane of Arthropods, the attack cooldown since his last blow on a box, a critical blow while falling (x1.5), Fire Aspect; the oils go to the carrier (potion/oil_hit)
scoreboard players operation #id le.l = @s le.lnk
execute on attacker run tag @s add le.chit
execute as @p[tag=le.chit] run function last_ember:lab/cent/blow
execute as @e[tag=le.cent] if score @s le.lnk = #id le.l unless score @s le.ls matches 3 run function last_ember:lab/cent/hurt with storage last_ember:lab cd
tag @a remove le.chit
data remove entity @s attack
data remove entity @s interaction
