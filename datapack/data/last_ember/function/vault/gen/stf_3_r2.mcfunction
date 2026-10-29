# Посох Пламенной Жатвы -> r2
scoreboard players set #p.3 le.vt 1
scoreboard players set #k le.vt 3
execute unless score #u.3 le.vt matches 1 run function last_ember:vault/gen/put_3
return 1
