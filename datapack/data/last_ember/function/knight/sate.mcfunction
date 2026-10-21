# as a player near the blessing knight: "sated by the bonfire" for 10 minutes (the food drains slower: +1 food every 40 s)
tag @s add le.sated
scoreboard players operation @s le.sat = #gt le.e
scoreboard players add @s le.sat 12000
scoreboard players set @s le.satcd 0
title @s actionbar {"text":"Благословение костра: сытость на 10 минут","color":"gold"}
