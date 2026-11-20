# T-027: as a spirit, every second: soul fire round the knights (the body unseen, the armour seen), the evil spirit lives 30 s
scoreboard players add @s le.cst 1
execute if entity @s[tag=le.cknight] run particle minecraft:soul ~ ~1 ~ 0.25 0.6 0.25 0.01 3 normal
execute if entity @s[tag=le.cvex] if score @s le.cst matches 30.. run function last_ember:cemetery/spirit_gone
