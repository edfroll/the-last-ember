# Посох Отринутой Тяжести -> r4
scoreboard players set #p.4 le.vt 1
scoreboard players set #k le.vt 4
execute unless score #u.4 le.vt matches 1 run function last_ember:vault/gen/put_4
return 1
