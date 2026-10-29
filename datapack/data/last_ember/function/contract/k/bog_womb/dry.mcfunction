tag @s add le.cdry
attribute @s minecraft:attack_damage modifier add last_ember:ct_dry -0.5 add_multiplied_base
attribute @s minecraft:armor modifier add last_ember:ct_dry -1 add_multiplied_total
effect clear @s minecraft:regeneration
playsound last_ember:creature.rotfiend.vo_dmg hostile @a ~ ~ ~ 1.6 0.7
