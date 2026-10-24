# MODULE (as a player): Blood — half a heart every 3 s for 12 s; crouching for 3 s (a bandage) stops it; another hit starts it over
tag @s add le.wound
scoreboard players set @s le.wbl 240
scoreboard players set @s le.wbs 0
title @s actionbar {"text":"Кровь! Присядь на 3 секунды — перевязка","color":"red"}
