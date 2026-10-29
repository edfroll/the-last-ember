# a player's own number (le.cpn) for the owners of trail branches
execute if score @s le.cpn matches 1.. run return 0
scoreboard players operation @s le.cpn = #pn_next le.ct
scoreboard players add #pn_next le.ct 1
