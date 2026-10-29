# Посох Изгнания -> r3
scoreboard players set #p.5 le.vt 1
scoreboard players set #k le.vt 5
execute unless score #u.5 le.vt matches 1 run function last_ember:vault/gen/put_5
return 1
