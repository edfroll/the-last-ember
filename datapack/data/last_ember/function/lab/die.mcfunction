# dead by our rules: frozen and invulnerable while it dies its own way (lab/<kind>/dying), then removed out of sight
scoreboard players set @s le.ls 3
scoreboard players set @s le.lt 0
data merge entity @s {NoAI:1b,Invulnerable:1b}
attribute @s minecraft:movement_speed modifier remove last_ember:lab_hold
