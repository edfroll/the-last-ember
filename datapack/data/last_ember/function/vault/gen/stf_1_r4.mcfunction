# Посох Мгновения -> r4
scoreboard players set #p.1 le.vt 1
scoreboard players set #k le.vt 1
execute unless score #u.1 le.vt matches 1 run function last_ember:vault/gen/put_4
return 1
