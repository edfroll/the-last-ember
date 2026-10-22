# T-014: called from last_ember:load
scoreboard objectives add le.el dummy
execute unless score #elitechance le.el matches 1.. run scoreboard players set #elitechance le.el 100
execute unless score #elimit_p le.el matches 1.. run scoreboard players set #elimit_p le.el 2
execute unless score #elimit_w le.el matches 1.. run scoreboard players set #elimit_w le.el 8
scoreboard players set #2 le.el 2
scoreboard players set #3 le.el 3
scoreboard players set #4 le.el 4
scoreboard players set #5 le.el 5
scoreboard players set #100 le.el 100
scoreboard players set #2000 le.el 2000
schedule function last_ember:elite/loop 40t replace
