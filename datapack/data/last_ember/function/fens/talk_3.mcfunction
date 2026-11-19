# T-026: the Crone, before the choice. The first talk: her introduction; with the skull: the give button; else "not yet"
execute unless entity @s[tag=le.fh3] run return run function last_ember:fens/intro_3
execute store result score #h le.fn run clear @s *[minecraft:custom_data~{le_citem:"fens_skull"}] 0
execute if score #h le.fn matches 1.. run scoreboard players enable @s le.fgive
execute if score #h le.fn matches 1.. run return run dialog show @s last_ember:fens/give_3
dialog show @s last_ember:fens/wait_3
