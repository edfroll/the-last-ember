execute unless entity @e[tag=le.lme,tag=le.contract] run damage @s 7 minecraft:mob_attack by @e[tag=le.lme,limit=1]
execute if entity @e[tag=le.lme,tag=le.contract] run function last_ember:contract/m/strike
playsound last_ember:creature.leshen.attack_roots_hit hostile @a ~ ~1 ~ 1.4 1
function last_ember:wound/roots
