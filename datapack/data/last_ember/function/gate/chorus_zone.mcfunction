# T-024: zones with the flag no_chorus (zones/zones.txt): the hop of a chorus fruit (more than 1 block sideways in one tick) goes back to
# where the fruit was eaten when it was eaten in such a zone, or when it lands in one (the flags are taken at the new place at once)
scoreboard players operation #dx le.gate = @s le.cnx
scoreboard players operation #dx le.gate -= @s le.cpx
scoreboard players operation #dz le.gate = @s le.cnz
scoreboard players operation #dz le.gate -= @s le.cpz
scoreboard players operation @s le.cpx = @s le.cnx
scoreboard players operation @s le.cpy = @s le.cny
scoreboard players operation @s le.cpz = @s le.cnz
execute if score #dx le.gate matches -10..10 if score #dz le.gate matches -10..10 run return 0
execute if entity @s[tag=le.chz] run return run function last_ember:gate/chorus_zone_back
function last_ember:zones/player
execute if entity @s[tag=le.zf.no_chorus] run function last_ember:gate/chorus_zone_back
