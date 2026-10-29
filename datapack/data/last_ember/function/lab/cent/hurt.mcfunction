# as the carrier: the blow of the player le.chit (lab/cent/blow); Fire Aspect sets it on fire (4 s a level); the oils of his weapon hit it
tag @s add le.chitv
$damage @s $(d) minecraft:player_attack by @p[tag=le.chit]
execute if score #fa le.l matches 1.. store result entity @s Fire short 80 run scoreboard players get #fa le.l
