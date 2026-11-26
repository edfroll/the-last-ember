# T-033: admin: the state of the mines
execute store result score #c le.mn if entity @e[type=minecraft:zombie,tag=le.mn_dead]
execute store result score #c2 le.mn if entity @e[type=minecraft:zombie,tag=le.mn_dead,tag=le.mna]
execute store result score #c3 le.mn if entity @e[type=minecraft:minecart,tag=le.mn_cart]
tellraw @s [{"text":"mines: cave-ins ","color":"gray"},{"score":{"name":"#c1","objective":"le.mn"}},{"text":" "},{"score":{"name":"#c2","objective":"le.mn"}},{"text":" "},{"score":{"name":"#c3","objective":"le.mn"}},{"text":", dead miners "},{"score":{"name":"#c","objective":"le.mn"}},{"text":" (awake "},{"score":{"name":"#c2","objective":"le.mn"}},{"text":"), bran "},{"score":{"name":"#bran","objective":"le.mn"}},{"text":", carts "},{"score":{"name":"#c3","objective":"le.mn"}}]
