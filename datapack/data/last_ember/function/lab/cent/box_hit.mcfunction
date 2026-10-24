# as a hit box punched by a player: the blow goes to the carrier with the player's attack damage
scoreboard players operation #id le.l = @s le.lnk
execute on attacker run tag @s add le.chit
execute on attacker store result storage last_ember:lab cd.d float 0.1 run attribute @s minecraft:attack_damage get 10
execute as @e[tag=le.cent] if score @s le.lnk = #id le.l unless score @s le.ls matches 3 run function last_ember:lab/cent/hurt with storage last_ember:lab cd
tag @a remove le.chit
data remove entity @s attack
data remove entity @s interaction
