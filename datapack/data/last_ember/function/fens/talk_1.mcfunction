# T-026: the Mother, before the choice. The first talk: her introduction (a healer also hears the recipe of the Clairvoyance);
# with the vial in the inventory: the give button; else "not yet"
execute unless entity @s[tag=le.fh1] if entity @s[tag=le.class.healer] run return run function last_ember:fens/intro_1h
execute unless entity @s[tag=le.fh1] run return run function last_ember:fens/intro_1
execute store result score #h le.fn run clear @s *[minecraft:custom_data~{le_citem:"fens_vial"}] 0
execute if score #h le.fn matches 1.. run scoreboard players enable @s le.fgive
execute if score #h le.fn matches 1.. run return run dialog show @s last_ember:fens/give_1
dialog show @s last_ember:fens/wait_1
