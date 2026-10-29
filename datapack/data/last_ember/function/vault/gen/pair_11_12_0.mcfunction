# Котёл Старой Знахарки -> r2, Сумка Травницы -> r4
scoreboard players set #k le.vt 11
execute unless score #u.11 le.vt matches 1 run function last_ember:vault/gen/put_3
scoreboard players set #k le.vt 12
execute unless score #u.12 le.vt matches 1 run function last_ember:vault/gen/put_4
