execute unless entity @e[tag=le.lme,tag=le.contract] run damage @s 6 minecraft:mob_attack by @e[tag=le.lme,limit=1]
execute if entity @e[tag=le.lme,tag=le.contract] run function last_ember:contract/m/strike
function last_ember:wound/blood
