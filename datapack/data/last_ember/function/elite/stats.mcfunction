# ADMIN: how many elites are alive, by regions (7 = the Nether, -1 = outside the regions): function last_ember:elite/stats
scoreboard players set #cnt_0 le.el 0
scoreboard players set #cnt_1 le.el 0
scoreboard players set #cnt_2 le.el 0
scoreboard players set #cnt_3 le.el 0
scoreboard players set #cnt_4 le.el 0
scoreboard players set #cnt_5 le.el 0
scoreboard players set #cnt_6 le.el 0
scoreboard players set #cnt_7 le.el 0
execute as @e[tag=le.elite] at @s run function last_ember:elite/stats_one
execute store result score #all le.el if entity @e[tag=le.elite]
tellraw @s [{"text":"Элит: ","color":"gold"},{"score":{"name":"#all","objective":"le.el"}},{"text":" (Р0 ","color":"gray"},{"score":{"name":"#cnt_0","objective":"le.el"}},{"text":", Р1 "},{"score":{"name":"#cnt_1","objective":"le.el"}},{"text":", Р2 "},{"score":{"name":"#cnt_2","objective":"le.el"}},{"text":", Р3 "},{"score":{"name":"#cnt_3","objective":"le.el"}},{"text":", Р4 "},{"score":{"name":"#cnt_4","objective":"le.el"}},{"text":", Р5 "},{"score":{"name":"#cnt_5","objective":"le.el"}},{"text":", Р6 "},{"score":{"name":"#cnt_6","objective":"le.el"}},{"text":", Незер "},{"score":{"name":"#cnt_7","objective":"le.el"}},{"text":")"}]
