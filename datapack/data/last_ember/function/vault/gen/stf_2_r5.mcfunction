# Посох Хладной Длани -> r5
scoreboard players set #p.2 le.vt 1
scoreboard players set #k le.vt 2
execute unless score #u.2 le.vt matches 1 run function last_ember:vault/gen/put_6
return 1
