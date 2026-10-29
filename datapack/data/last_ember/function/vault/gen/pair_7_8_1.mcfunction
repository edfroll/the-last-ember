# Щит Стража -> r4, Латы Последнего Дозора -> r2
scoreboard players set #k le.vt 7
execute unless score #u.7 le.vt matches 1 run function last_ember:vault/gen/put_4
scoreboard players set #k le.vt 8
execute unless score #u.8 le.vt matches 1 run function last_ember:vault/gen/put_3
