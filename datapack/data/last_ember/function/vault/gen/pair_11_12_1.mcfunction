# Котёл Старой Знахарки -> r4, Сумка Травницы -> r2
scoreboard players set #k le.vt 11
execute unless score #u.11 le.vt matches 1 run function last_ember:vault/gen/put_4
scoreboard players set #k le.vt 12
execute unless score #u.12 le.vt matches 1 run function last_ember:vault/gen/put_3
