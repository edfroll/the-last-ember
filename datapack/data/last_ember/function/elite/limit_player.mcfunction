execute store result score #pc le.el if entity @e[tag=le.elite,distance=..48]
execute if score #pc le.el >= #elimit_p le.el run scoreboard players set #full le.el 1
