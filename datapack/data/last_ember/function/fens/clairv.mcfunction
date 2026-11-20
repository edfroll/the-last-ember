# T-026: advancement reward: a player drank the Clairvoyance (the healer's cauldron: lily pad + spider eye + slime): 90 s of the trails
advancement revoke @s only last_ember:fens/clairv
execute store result score @s le.fcl run time query gametime
scoreboard players add @s le.fcl 1800
playsound minecraft:block.amethyst_block.resonate player @s ~ ~ ~ 0.8 0.6
title @s actionbar {"text":"Вода смотрит на тебя. Теперь и ты на неё.","color":"dark_aqua"}
