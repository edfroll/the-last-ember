# as a player: #xt le.e = all the experience points (vanilla level formulas + the points of the current level)
execute store result score #lv le.e run experience query @s levels
execute store result score #pt le.e run experience query @s points
execute if score #lv le.e matches ..16 run function last_ember:seer/xt_a
execute if score #lv le.e matches 17..31 run function last_ember:seer/xt_b
execute if score #lv le.e matches 32.. run function last_ember:seer/xt_c
scoreboard players operation #xt le.e += #pt le.e
