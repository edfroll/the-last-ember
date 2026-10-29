# Посох Мгновения -> r5
scoreboard players set #p.1 le.vt 1
scoreboard players set #k le.vt 1
execute unless score #u.1 le.vt matches 1 run function last_ember:vault/gen/put_6
return 1
