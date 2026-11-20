# T-027: a player rang a bell (vanilla statistic): the lodge bell, not on its cooldown (5 min) -> the unrest -4, every spirit leaves,
# the line for the players at the cemetery
scoreboard players set @s le.cbell 0
execute unless function last_ember:cemetery/gen/bell_near run return 0
execute if score #gt le.cem < #bellcd le.cem run return 0
scoreboard players operation #bellcd le.cem = #gt le.cem
scoreboard players add #bellcd le.cem 6000
scoreboard players remove #dist le.cem 4
execute if score #dist le.cem matches ..-1 run scoreboard players set #dist le.cem 0
execute as @e[tag=le.cspirit] at @s run function last_ember:cemetery/spirit_gone
function last_ember:cemetery/gen/players_cem
function last_ember:cemetery/save
